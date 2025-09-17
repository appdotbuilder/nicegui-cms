from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for role and content status
class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Association table for many-to-many relationship between posts and tags
class PostTagLink(SQLModel, table=True):
    __tablename__ = "post_tag_links"  # type: ignore[assignment]

    post_id: Optional[int] = Field(default=None, foreign_key="posts.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


# Association table for many-to-many relationship between pages and tags
class PageTagLink(SQLModel, table=True):
    __tablename__ = "page_tag_links"  # type: ignore[assignment]

    page_id: Optional[int] = Field(default=None, foreign_key="pages.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.EDITOR)
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    pages: List["Page"] = Relationship(back_populates="author")
    categories: List["Category"] = Relationship(back_populates="created_by")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    slug: str = Field(unique=True, max_length=100)
    description: str = Field(default="", max_length=500)
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    created_by_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    created_by: User = Relationship(back_populates="categories")
    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    posts: List["Post"] = Relationship(back_populates="category")
    pages: List["Page"] = Relationship(back_populates="category")


class Tag(SQLModel, table=True):
    __tablename__ = "tags"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=50)
    slug: str = Field(unique=True, max_length=50)
    description: str = Field(default="", max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    posts: List["Post"] = Relationship(back_populates="tags", link_model=PostTagLink)
    pages: List["Page"] = Relationship(back_populates="tags", link_model=PageTagLink)


class Post(SQLModel, table=True):
    __tablename__ = "posts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    slug: str = Field(unique=True, max_length=200)
    excerpt: str = Field(default="", max_length=500)
    content: str = Field(default="")
    featured_image_url: Optional[str] = Field(default=None, max_length=500)
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    is_featured: bool = Field(default=False)
    view_count: int = Field(default=0)
    author_id: int = Field(foreign_key="users.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    published_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_title: Optional[str] = Field(default=None, max_length=200)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    seo_keywords: List[str] = Field(default=[], sa_column=Column(JSON))

    # Relationships
    author: User = Relationship(back_populates="posts")
    category: Optional[Category] = Relationship(back_populates="posts")
    tags: List[Tag] = Relationship(back_populates="posts", link_model=PostTagLink)


class Page(SQLModel, table=True):
    __tablename__ = "pages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    slug: str = Field(unique=True, max_length=200)
    content: str = Field(default="")
    template: str = Field(default="default", max_length=50)
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    is_homepage: bool = Field(default=False)
    sort_order: int = Field(default=0)
    author_id: int = Field(foreign_key="users.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="pages.id")
    published_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_title: Optional[str] = Field(default=None, max_length=200)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    custom_fields: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    author: User = Relationship(back_populates="pages")
    category: Optional[Category] = Relationship(back_populates="pages")
    parent: Optional["Page"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Page.id"}
    )
    children: List["Page"] = Relationship(back_populates="parent")
    tags: List[Tag] = Relationship(back_populates="pages", link_model=PageTagLink)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.EDITOR)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class UserLogin(SQLModel, table=False):
    username: str
    password: str


class UserResponse(SQLModel, table=False):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    last_login: Optional[str] = None
    created_at: str


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    parent_id: Optional[int] = Field(default=None)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    slug: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[int] = Field(default=None)


class CategoryResponse(SQLModel, table=False):
    id: int
    name: str
    slug: str
    description: str
    parent_id: Optional[int]
    created_at: str
    updated_at: str


class TagCreate(SQLModel, table=False):
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50)
    description: str = Field(default="", max_length=200)


class TagUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=50)
    slug: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)


class TagResponse(SQLModel, table=False):
    id: int
    name: str
    slug: str
    description: str
    created_at: str


class PostCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    slug: str = Field(max_length=200)
    excerpt: str = Field(default="", max_length=500)
    content: str = Field(default="")
    featured_image_url: Optional[str] = Field(default=None, max_length=500)
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    is_featured: bool = Field(default=False)
    category_id: Optional[int] = Field(default=None)
    tag_ids: List[int] = Field(default=[])
    meta_title: Optional[str] = Field(default=None, max_length=200)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    seo_keywords: List[str] = Field(default=[])


class PostUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=200)
    excerpt: Optional[str] = Field(default=None, max_length=500)
    content: Optional[str] = Field(default=None)
    featured_image_url: Optional[str] = Field(default=None, max_length=500)
    status: Optional[ContentStatus] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    tag_ids: Optional[List[int]] = Field(default=None)
    meta_title: Optional[str] = Field(default=None, max_length=200)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    seo_keywords: Optional[List[str]] = Field(default=None)


class PostResponse(SQLModel, table=False):
    id: int
    title: str
    slug: str
    excerpt: str
    content: str
    featured_image_url: Optional[str]
    status: ContentStatus
    is_featured: bool
    view_count: int
    author_id: int
    category_id: Optional[int]
    published_at: Optional[str]
    created_at: str
    updated_at: str
    meta_title: Optional[str]
    meta_description: Optional[str]
    seo_keywords: List[str]


class PageCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    slug: str = Field(max_length=200)
    content: str = Field(default="")
    template: str = Field(default="default", max_length=50)
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    is_homepage: bool = Field(default=False)
    sort_order: int = Field(default=0)
    category_id: Optional[int] = Field(default=None)
    parent_id: Optional[int] = Field(default=None)
    tag_ids: List[int] = Field(default=[])
    meta_title: Optional[str] = Field(default=None, max_length=200)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    custom_fields: Dict[str, Any] = Field(default={})


class PageUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = Field(default=None)
    template: Optional[str] = Field(default=None, max_length=50)
    status: Optional[ContentStatus] = Field(default=None)
    is_homepage: Optional[bool] = Field(default=None)
    sort_order: Optional[int] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    parent_id: Optional[int] = Field(default=None)
    tag_ids: Optional[List[int]] = Field(default=None)
    meta_title: Optional[str] = Field(default=None, max_length=200)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    custom_fields: Optional[Dict[str, Any]] = Field(default=None)


class PageResponse(SQLModel, table=False):
    id: int
    title: str
    slug: str
    content: str
    template: str
    status: ContentStatus
    is_homepage: bool
    sort_order: int
    author_id: int
    category_id: Optional[int]
    parent_id: Optional[int]
    published_at: Optional[str]
    created_at: str
    updated_at: str
    meta_title: Optional[str]
    meta_description: Optional[str]
    custom_fields: Dict[str, Any]
