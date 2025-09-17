from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for role-based access control and content status
class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(str, Enum):
    POST = "post"
    PAGE = "page"


# Many-to-many relationship tables
class PostCategory(SQLModel, table=True):
    __tablename__ = "post_categories"  # type: ignore[assignment]

    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    category_id: int = Field(foreign_key="categories.id", primary_key=True)


class PostTag(SQLModel, table=True):
    __tablename__ = "post_tags"  # type: ignore[assignment]

    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


# User management with authentication and role-based access
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50, index=True)
    email: str = Field(
        unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", index=True
    )
    password_hash: str = Field(max_length=255)  # Hashed password for security
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.EDITOR)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)

    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    pages: List["Page"] = Relationship(back_populates="author")


# Category taxonomy for organizing content
class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    slug: str = Field(max_length=120, unique=True, index=True)
    description: str = Field(default="", max_length=500)
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    posts: List["Post"] = Relationship(back_populates="categories", link_model=PostCategory)


# Tag taxonomy for flexible content labeling
class Tag(SQLModel, table=True):
    __tablename__ = "tags"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    slug: str = Field(max_length=120, unique=True, index=True)
    description: str = Field(default="", max_length=500)
    color: str = Field(default="#6B7280", max_length=7)  # Hex color for UI display
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    posts: List["Post"] = Relationship(back_populates="tags", link_model=PostTag)


# Post content model for blog posts and articles
class Post(SQLModel, table=True):
    __tablename__ = "posts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=300, unique=True, index=True)
    content: str = Field(default="")
    excerpt: str = Field(default="", max_length=500)  # Short summary
    status: ContentStatus = Field(default=ContentStatus.DRAFT, index=True)
    featured_image: Optional[str] = Field(default=None, max_length=500)  # URL to featured image
    meta_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # SEO and custom fields
    view_count: int = Field(default=0)
    is_featured: bool = Field(default=False)
    allow_comments: bool = Field(default=True)
    author_id: int = Field(foreign_key="users.id", index=True)
    published_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    author: User = Relationship(back_populates="posts")
    categories: List[Category] = Relationship(back_populates="posts", link_model=PostCategory)
    tags: List[Tag] = Relationship(back_populates="tags", link_model=PostTag)
    comments: List["Comment"] = Relationship(back_populates="post")


# Page content model for static pages
class Page(SQLModel, table=True):
    __tablename__ = "pages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=300, unique=True, index=True)
    content: str = Field(default="")
    status: ContentStatus = Field(default=ContentStatus.DRAFT, index=True)
    meta_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # SEO and custom fields
    template: str = Field(default="default", max_length=100)  # Template name for rendering
    parent_id: Optional[int] = Field(default=None, foreign_key="pages.id")
    sort_order: int = Field(default=0)  # For menu ordering
    is_in_menu: bool = Field(default=False)
    author_id: int = Field(foreign_key="users.id", index=True)
    published_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    author: User = Relationship(back_populates="pages")
    parent: Optional["Page"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Page.id"}
    )
    children: List["Page"] = Relationship(back_populates="parent")


# Comment system for posts
class Comment(SQLModel, table=True):
    __tablename__ = "comments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    author_name: str = Field(max_length=100)
    author_email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    author_website: Optional[str] = Field(default=None, max_length=500)
    content: str = Field(max_length=2000)
    is_approved: bool = Field(default=False, index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    post: Post = Relationship(back_populates="comments")
    parent: Optional["Comment"] = Relationship(
        back_populates="replies", sa_relationship_kwargs={"remote_side": "Comment.id"}
    )
    replies: List["Comment"] = Relationship(back_populates="parent")


# Media management for file uploads
class Media(SQLModel, table=True):
    __tablename__ = "media"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255, index=True)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_url: str = Field(max_length=500)
    mime_type: str = Field(max_length=100)
    file_size: int = Field(default=0)  # Size in bytes
    alt_text: str = Field(default="", max_length=255)  # For accessibility
    caption: str = Field(default="", max_length=500)
    meta_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # EXIF data, dimensions, etc.
    uploaded_by: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    uploader: User = Relationship()


# Non-persistent schemas for API requests/responses and validation


# User schemas
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)  # Plain password - will be hashed
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
    created_at: str  # ISO format
    last_login: Optional[str] = None  # ISO format


# Post schemas
class PostCreate(SQLModel, table=False):
    title: str = Field(max_length=255)
    slug: str = Field(max_length=300)
    content: str = Field(default="")
    excerpt: str = Field(default="", max_length=500)
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    featured_image: Optional[str] = Field(default=None, max_length=500)
    meta_data: Dict[str, Any] = Field(default={})
    is_featured: bool = Field(default=False)
    allow_comments: bool = Field(default=True)
    category_ids: List[int] = Field(default=[])
    tag_ids: List[int] = Field(default=[])


class PostUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=300)
    content: Optional[str] = Field(default=None)
    excerpt: Optional[str] = Field(default=None, max_length=500)
    status: Optional[ContentStatus] = Field(default=None)
    featured_image: Optional[str] = Field(default=None, max_length=500)
    meta_data: Optional[Dict[str, Any]] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)
    allow_comments: Optional[bool] = Field(default=None)
    category_ids: Optional[List[int]] = Field(default=None)
    tag_ids: Optional[List[int]] = Field(default=None)


class PostResponse(SQLModel, table=False):
    id: int
    title: str
    slug: str
    content: str
    excerpt: str
    status: ContentStatus
    featured_image: Optional[str] = None
    meta_data: Dict[str, Any]
    view_count: int
    is_featured: bool
    allow_comments: bool
    author_id: int
    published_at: Optional[str] = None  # ISO format
    created_at: str  # ISO format
    updated_at: str  # ISO format


# Page schemas
class PageCreate(SQLModel, table=False):
    title: str = Field(max_length=255)
    slug: str = Field(max_length=300)
    content: str = Field(default="")
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    meta_data: Dict[str, Any] = Field(default={})
    template: str = Field(default="default", max_length=100)
    parent_id: Optional[int] = Field(default=None)
    sort_order: int = Field(default=0)
    is_in_menu: bool = Field(default=False)


class PageUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=300)
    content: Optional[str] = Field(default=None)
    status: Optional[ContentStatus] = Field(default=None)
    meta_data: Optional[Dict[str, Any]] = Field(default=None)
    template: Optional[str] = Field(default=None, max_length=100)
    parent_id: Optional[int] = Field(default=None)
    sort_order: Optional[int] = Field(default=None)
    is_in_menu: Optional[bool] = Field(default=None)


class PageResponse(SQLModel, table=False):
    id: int
    title: str
    slug: str
    content: str
    status: ContentStatus
    meta_data: Dict[str, Any]
    template: str
    parent_id: Optional[int] = None
    sort_order: int
    is_in_menu: bool
    author_id: int
    published_at: Optional[str] = None  # ISO format
    created_at: str  # ISO format
    updated_at: str  # ISO format


# Category schemas
class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=120)
    description: str = Field(default="", max_length=500)
    parent_id: Optional[int] = Field(default=None)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    slug: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class CategoryResponse(SQLModel, table=False):
    id: int
    name: str
    slug: str
    description: str
    parent_id: Optional[int] = None
    is_active: bool
    created_at: str  # ISO format


# Tag schemas
class TagCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=120)
    description: str = Field(default="", max_length=500)
    color: str = Field(default="#6B7280", max_length=7)


class TagUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    slug: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    color: Optional[str] = Field(default=None, max_length=7)
    is_active: Optional[bool] = Field(default=None)


class TagResponse(SQLModel, table=False):
    id: int
    name: str
    slug: str
    description: str
    color: str
    is_active: bool
    created_at: str  # ISO format


# Comment schemas
class CommentCreate(SQLModel, table=False):
    post_id: int
    author_name: str = Field(max_length=100)
    author_email: str = Field(max_length=255)
    author_website: Optional[str] = Field(default=None, max_length=500)
    content: str = Field(max_length=2000)
    parent_id: Optional[int] = Field(default=None)


class CommentUpdate(SQLModel, table=False):
    content: Optional[str] = Field(default=None, max_length=2000)
    is_approved: Optional[bool] = Field(default=None)


class CommentResponse(SQLModel, table=False):
    id: int
    post_id: int
    author_name: str
    author_email: str
    author_website: Optional[str] = None
    content: str
    is_approved: bool
    parent_id: Optional[int] = None
    created_at: str  # ISO format


# Media schemas
class MediaCreate(SQLModel, table=False):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_url: str = Field(max_length=500)
    mime_type: str = Field(max_length=100)
    file_size: int
    alt_text: str = Field(default="", max_length=255)
    caption: str = Field(default="", max_length=500)
    meta_data: Dict[str, Any] = Field(default={})


class MediaUpdate(SQLModel, table=False):
    alt_text: Optional[str] = Field(default=None, max_length=255)
    caption: Optional[str] = Field(default=None, max_length=500)
    meta_data: Optional[Dict[str, Any]] = Field(default=None)


class MediaResponse(SQLModel, table=False):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_url: str
    mime_type: str
    file_size: int
    alt_text: str
    caption: str
    meta_data: Dict[str, Any]
    uploaded_by: int
    created_at: str  # ISO format
