# Narrative OS - Implementation Roadmap (MVP → v1.0)

**Timeline:** 8 weeks
**Goal:** Production-ready platform with full competitive feature set
**Team:** 2-3 full-stack engineers + 1 DevOps (part-time)

---

## Week 1: Security & Authentication Foundation 🔒

### Day 1-2: Authentication System (Backend)

**Task 1.1: User Model & Database Schema**
```python
# backend/core/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    STUDIO = "studio"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100))
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)

    # Relationships
    projects = relationship("Project", back_populates="owner")
    collaborations = relationship("ProjectCollaborator", back_populates="user")

class ProjectCollaborator(Base, TimestampMixin):
    __tablename__ = "project_collaborators"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(CollaboratorRole), nullable=False)

    project = relationship("Project", back_populates="collaborators")
    user = relationship("User", back_populates="collaborations")

# Migration
# alembic revision --autogenerate -m "Add user authentication tables"
```

**Task 1.2: JWT Authentication Service**
```python
# backend/core/auth/service.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def authenticate_user(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

# Dependency for protected routes
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

**Task 1.3: Auth API Routes**
```python
# backend/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = AuthService.get_password_hash(data.password)
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hashed_password,
        subscription_tier=SubscriptionTier.FREE
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # TODO: Send verification email
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService()
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = auth_service.create_access_token(data={"sub": user.id})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        access_token = AuthService.create_access_token(data={"sub": user.id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

### Day 3: Authorization & Permissions

**Task 1.4: Project Permissions Middleware**
```python
# backend/core/auth/permissions.py
from enum import Enum

class CollaboratorRole(Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class Permission(Enum):
    READ_PROJECT = "read_project"
    EDIT_PROJECT = "edit_project"
    DELETE_PROJECT = "delete_project"
    MANAGE_COLLABORATORS = "manage_collaborators"
    GENERATE_PROSE = "generate_prose"

ROLE_PERMISSIONS = {
    CollaboratorRole.OWNER: [
        Permission.READ_PROJECT,
        Permission.EDIT_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.MANAGE_COLLABORATORS,
        Permission.GENERATE_PROSE,
    ],
    CollaboratorRole.EDITOR: [
        Permission.READ_PROJECT,
        Permission.EDIT_PROJECT,
        Permission.GENERATE_PROSE,
    ],
    CollaboratorRole.VIEWER: [
        Permission.READ_PROJECT,
    ],
}

async def check_project_permission(
    project_id: int,
    user: User,
    required_permission: Permission,
    db: Session
) -> bool:
    # Check if owner
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id == user.id:
        return True  # Owner has all permissions

    # Check collaborator role
    collab = db.query(ProjectCollaborator).filter(
        ProjectCollaborator.project_id == project_id,
        ProjectCollaborator.user_id == user.id
    ).first()

    if not collab:
        raise HTTPException(status_code=403, detail="Access denied")

    if required_permission in ROLE_PERMISSIONS[collab.role]:
        return True

    raise HTTPException(status_code=403, detail="Insufficient permissions")

# Dependency for protected project routes
def require_project_permission(permission: Permission):
    async def permission_checker(
        project_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        await check_project_permission(project_id, user, permission, db)
        return user
    return permission_checker
```

**Task 1.5: Update All API Routes with Auth**
```python
# Example: backend/api/routes/canon.py
@router.post("/character", response_model=CharacterResponse, status_code=201)
async def create_character(
    data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check project permission
    await check_project_permission(
        data.project_id,
        current_user,
        Permission.EDIT_PROJECT,
        db
    )

    # Create character
    character = CanonService(db).create_entity("character", data.project_id, data.dict())
    return character
```

### Day 4-5: Frontend Authentication

**Task 1.6: Auth Context & Token Management**
```typescript
// frontend/src/lib/auth.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from './api'

interface User {
  id: number
  email: string
  name: string
  subscription_tier: 'free' | 'pro' | 'studio'
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)

        const response = await api.post('/api/auth/login', formData)
        const { access_token, refresh_token, user } = response.data

        set({
          user,
          accessToken: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
        })

        // Set token in axios default headers
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      },

      register: async (email, password, name) => {
        const response = await api.post('/api/auth/register', {
          email,
          password,
          name,
        })
        // Auto-login after registration
        await get().login(email, password)
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        delete api.defaults.headers.common['Authorization']
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get()
        if (!refreshToken) throw new Error('No refresh token')

        const response = await api.post('/api/auth/refresh', {
          refresh_token: refreshToken,
        })
        const { access_token } = response.data

        set({ accessToken: access_token })
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)

// Axios interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        await useAuth.getState().refreshAccessToken()
        return api(originalRequest)
      } catch (refreshError) {
        useAuth.getState().logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)
```

**Task 1.7: Login/Register Pages**
```typescript
// frontend/src/app/login/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import Input from '@/components/Input'
import Button from '@/components/Button'

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login(email, password)
      router.push('/') // Redirect to home
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8 p-8">
        <div>
          <h2 className="text-3xl font-bold text-center">Sign in to Narrative OS</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="email"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <div className="text-sm text-red-600">{error}</div>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>

        <div className="text-center">
          <a href="/register" className="text-sm text-blue-600 hover:underline">
            Don't have an account? Sign up
          </a>
        </div>
      </div>
    </div>
  )
}
```

**Task 1.8: Protected Route HOC**
```typescript
// frontend/src/components/ProtectedRoute.tsx
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  if (!isAuthenticated) {
    return <div>Loading...</div>
  }

  return <>{children}</>
}
```

### Day 5: Soft Deletes & Audit Trail

**Task 1.9: Add Soft Delete Mixin**
```python
# backend/core/models/base.py
class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

# Update all models to inherit SoftDeleteMixin
class Character(Base, CanonEntityMixin, SoftDeleteMixin):
    # ... existing fields

# Update queries to filter out deleted records
def get_all_characters(db: Session, project_id: int):
    return db.query(Character).filter(
        Character.project_id == project_id,
        Character.deleted_at.is_(None)
    ).all()

# Soft delete method
def soft_delete(db: Session, entity, user_id: int):
    entity.deleted_at = datetime.utcnow()
    entity.deleted_by = user_id
    db.commit()
```

**Task 1.10: Audit Trail System**
```python
# backend/core/models/audit.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

# Decorator for audited actions
def audited(entity_type: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the function
            result = await func(*args, **kwargs)

            # Log to audit trail
            # Get user from context
            user = kwargs.get('current_user')
            if user:
                audit_log = AuditLog(
                    user_id=user.id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=result.id,
                    new_value=result.dict() if hasattr(result, 'dict') else None,
                )
                db.add(audit_log)
                db.commit()

            return result
        return wrapper
    return decorator
```

---

## Week 2: Export Service & Core Features 📄

### Day 1-3: Export Service Implementation

**Task 2.1: Export Service Backend**
```python
# backend/services/export/service.py
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from ebooklib import epub
import io

class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def export_docx(
        self,
        project_id: int,
        options: ExportOptions
    ) -> bytes:
        """Generate DOCX file from project chapters"""

        # Create document
        doc = Document()

        # Set margins and styles
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1.25)
            section.right_margin = Inches(1.25)

        # Add title
        project = self.db.query(Project).filter(Project.id == project_id).first()
        title = doc.add_heading(project.name, 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add author
        if options.include_author:
            author = doc.add_paragraph(f"by {project.owner.name}")
            author.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_page_break()

        # Add table of contents
        if options.include_toc:
            doc.add_heading('Table of Contents', level=1)
            chapters = self.db.query(Chapter).filter(
                Chapter.project_id == project_id,
                Chapter.deleted_at.is_(None)
            ).order_by(Chapter.chapter_number).all()

            for chapter in chapters:
                toc_entry = doc.add_paragraph(
                    f"Chapter {chapter.chapter_number}: {chapter.title or 'Untitled'}"
                )
                toc_entry.style = 'TOC 1'
            doc.add_page_break()

        # Add chapters
        chapters = self.db.query(Chapter).filter(
            Chapter.project_id == project_id,
            Chapter.deleted_at.is_(None)
        ).order_by(Chapter.chapter_number).all()

        for chapter in chapters:
            # Chapter heading
            doc.add_heading(
                f"Chapter {chapter.chapter_number}" +
                (f": {chapter.title}" if chapter.title else ""),
                level=1
            )

            # Get scenes
            scenes = self.db.query(Scene).filter(
                Scene.chapter_id == chapter.id,
                Scene.deleted_at.is_(None)
            ).order_by(Scene.scene_number).all()

            for i, scene in enumerate(scenes):
                if scene.prose:
                    # Add scene prose
                    doc.add_paragraph(scene.prose)

                    # Scene break (except last scene)
                    if i < len(scenes) - 1 and options.scene_breaks:
                        break_para = doc.add_paragraph("* * *")
                        break_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Chapter break
            if chapter != chapters[-1]:
                doc.add_page_break()

        # Save to bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def export_epub(
        self,
        project_id: int,
        metadata: BookMetadata
    ) -> bytes:
        """Generate EPUB file from project chapters"""

        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Create EPUB book
        book = epub.EpubBook()

        # Set metadata
        book.set_identifier(f'narrative-os-{project_id}')
        book.set_title(metadata.title or project.name)
        book.set_language(metadata.language or 'en')

        if metadata.author:
            book.add_author(metadata.author)

        # Add cover if provided
        if metadata.cover_image:
            book.set_cover('cover.jpg', metadata.cover_image)

        # Add chapters
        chapters_list = self.db.query(Chapter).filter(
            Chapter.project_id == project_id,
            Chapter.deleted_at.is_(None)
        ).order_by(Chapter.chapter_number).all()

        epub_chapters = []
        spine = ['nav']

        for chapter in chapters_list:
            # Get scenes
            scenes = self.db.query(Scene).filter(
                Scene.chapter_id == chapter.id,
                Scene.deleted_at.is_(None)
            ).order_by(Scene.scene_number).all()

            # Build chapter content
            content = f'<h1>Chapter {chapter.chapter_number}</h1>'
            if chapter.title:
                content += f'<h2>{chapter.title}</h2>'

            for scene in scenes:
                if scene.prose:
                    # Convert prose to HTML paragraphs
                    paragraphs = scene.prose.split('\n\n')
                    for para in paragraphs:
                        content += f'<p>{para}</p>'

            # Create EPUB chapter
            epub_chapter = epub.EpubHtml(
                title=f'Chapter {chapter.chapter_number}',
                file_name=f'chap_{chapter.chapter_number:03d}.xhtml',
                lang='en'
            )
            epub_chapter.content = content

            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
            spine.append(epub_chapter)

        # Add table of contents
        book.toc = tuple(epub_chapters)

        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define CSS
        style = '''
        body { font-family: Georgia, serif; }
        h1 { text-align: center; }
        h2 { text-align: center; font-style: italic; }
        p { text-indent: 1.5em; margin: 0; }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)

        # Set spine
        book.spine = spine

        # Write to bytes
        buffer = io.BytesIO()
        epub.write_epub(buffer, book)
        buffer.seek(0)
        return buffer.getvalue()
```

**Task 2.2: Export API Routes**
```python
# backend/api/routes/export.py
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/export", tags=["Export"])

@router.post("/docx")
async def export_docx(
    data: ExportDOCXRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check permission
    await check_project_permission(
        data.project_id,
        current_user,
        Permission.READ_PROJECT,
        db
    )

    # Generate DOCX
    service = ExportService(db)
    docx_bytes = service.export_docx(data.project_id, data.options)

    # Return as download
    project = db.query(Project).filter(Project.id == data.project_id).first()
    filename = f"{project.name.replace(' ', '_')}.docx"

    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/epub")
async def export_epub(
    data: ExportEPUBRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check permission
    await check_project_permission(
        data.project_id,
        current_user,
        Permission.READ_PROJECT,
        db
    )

    # Generate EPUB
    service = ExportService(db)
    epub_bytes = service.export_epub(data.project_id, data.metadata)

    # Return as download
    filename = f"{data.metadata.title.replace(' ', '_')}.epub"

    return StreamingResponse(
        io.BytesIO(epub_bytes),
        media_type="application/epub+zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

**Task 2.3: Export UI Component**
```typescript
// frontend/src/components/ExportModal.tsx
'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import Button from './Button'
import Input from './Input'
import api from '@/lib/api'

interface ExportModalProps {
  projectId: number
  projectName: string
  onClose: () => void
}

export default function ExportModal({ projectId, projectName, onClose }: ExportModalProps) {
  const [format, setFormat] = useState<'docx' | 'epub'>('docx')
  const [loading, setLoading] = useState(false)
  const [options, setOptions] = useState({
    include_toc: true,
    include_author: true,
    scene_breaks: true,
  })

  const handleExport = async () => {
    setLoading(true)
    try {
      const endpoint = format === 'docx' ? '/api/export/docx' : '/api/export/epub'
      const response = await api.post(endpoint, {
        project_id: projectId,
        options: format === 'docx' ? options : undefined,
        metadata: format === 'epub' ? {
          title: projectName,
          author: 'Your Name', // TODO: Get from user profile
          language: 'en'
        } : undefined
      }, {
        responseType: 'blob'
      })

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${projectName}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()

      onClose()
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Export Project</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Format</label>
              <div className="flex space-x-4 mt-2">
                <button
                  onClick={() => setFormat('docx')}
                  className={`flex-1 py-2 px-4 rounded ${
                    format === 'docx'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                >
                  DOCX
                </button>
                <button
                  onClick={() => setFormat('epub')}
                  className={`flex-1 py-2 px-4 rounded ${
                    format === 'epub'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                >
                  EPUB
                </button>
              </div>
            </div>

            {format === 'docx' && (
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={options.include_toc}
                    onChange={(e) =>
                      setOptions({ ...options, include_toc: e.target.checked })
                    }
                  />
                  <span className="text-sm">Include Table of Contents</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={options.include_author}
                    onChange={(e) =>
                      setOptions({ ...options, include_author: e.target.checked })
                    }
                  />
                  <span className="text-sm">Include Author Name</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={options.scene_breaks}
                    onChange={(e) =>
                      setOptions({ ...options, scene_breaks: e.target.checked })
                    }
                  />
                  <span className="text-sm">Add Scene Breaks (***)</span>
                </label>
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={handleExport} disabled={loading}>
                {loading ? 'Exporting...' : 'Export'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Day 4: Scene Creation UI

**Task 2.4: Scene Form Component**
```typescript
// frontend/src/components/planner/SceneForm.tsx
'use client'

import { useState } from 'react'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Textarea from '@/components/Textarea'
import { X } from 'lucide-react'

interface SceneFormProps {
  projectId: number
  chapterId: number
  nextSceneNumber: number
  onClose: () => void
}

export default function SceneForm({
  projectId,
  chapterId,
  nextSceneNumber,
  onClose,
}: SceneFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    scene_number: nextSceneNumber,
    goal: '',
    conflict: '',
    entering_value: 'hope',
    exiting_value: 'fear',
    what_changes: '',
    participants: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        project_id: projectId,
        chapter_id: chapterId,
        scene_number: formData.scene_number,
        goal: formData.goal,
        conflict: formData.conflict || undefined,
        entering_value: formData.entering_value,
        exiting_value: formData.exiting_value,
        what_changes: formData.what_changes,
        participants: formData.participants.split('\n').filter((p) => p.trim()),
      }

      await api.post('/api/planner/scene', payload)
      onClose()
    } catch (error) {
      console.error('Failed to create scene:', error)
      alert('Failed to create scene. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">New Scene</h3>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            type="number"
            label="Scene Number *"
            value={formData.scene_number}
            onChange={(e) =>
              setFormData({
                ...formData,
                scene_number: parseInt(e.target.value),
              })
            }
            required
          />
          <div className="col-span-2" />
        </div>

        <Textarea
          label="Goal *"
          placeholder="What is the character trying to achieve in this scene?"
          value={formData.goal}
          onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
          rows={2}
          required
        />

        <Textarea
          label="Conflict"
          placeholder="What prevents the character from achieving their goal?"
          value={formData.conflict}
          onChange={(e) => setFormData({ ...formData, conflict: e.target.value })}
          rows={2}
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Entering Value *"
            placeholder="e.g., hope, peace, confidence"
            value={formData.entering_value}
            onChange={(e) =>
              setFormData({ ...formData, entering_value: e.target.value })
            }
            required
          />
          <Input
            label="Exiting Value *"
            placeholder="e.g., fear, chaos, doubt"
            value={formData.exiting_value}
            onChange={(e) =>
              setFormData({ ...formData, exiting_value: e.target.value })
            }
            required
          />
        </div>

        <Textarea
          label="What Changes *"
          placeholder="What's different at the end of this scene?"
          value={formData.what_changes}
          onChange={(e) =>
            setFormData({ ...formData, what_changes: e.target.value })
          }
          rows={2}
          required
        />

        <Textarea
          label="Participants"
          placeholder="Character names (one per line)"
          value={formData.participants}
          onChange={(e) =>
            setFormData({ ...formData, participants: e.target.value })
          }
          rows={3}
        />

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Scene'}
          </Button>
        </div>
      </form>
    </div>
  )
}
```

**Task 2.5: Integrate Scene Form in ChapterList**
```typescript
// Update frontend/src/components/planner/ChapterList.tsx
// Add scene creation button and form
{isExpanded && (
  <div className="px-4 pb-4 space-y-2">
    <div className="flex items-center justify-between mb-3 pt-2 border-t border-gray-200 dark:border-gray-700">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Scene Cards
      </h4>
      <Button
        size="sm"
        onClick={() => setCreatingScene(chapter.id)}
      >
        <Plus className="h-4 w-4 mr-1" />
        Add Scene
      </Button>
    </div>

    {creatingScene === chapter.id && (
      <SceneForm
        projectId={projectId}
        chapterId={chapter.id}
        nextSceneNumber={(scenes[scenes.length - 1]?.scene_number || 0) + 1}
        onClose={() => {
          setCreatingScene(null)
          onUpdate()
        }}
      />
    )}

    {/* ... existing scene cards */}
  </div>
)}
```

### Day 5: Remaining Canon Entity Forms

**Task 2.6: Create Faction/Magic/Item/Event Forms**
```typescript
// frontend/src/components/canon/FactionForm.tsx
// Similar structure to CharacterForm with faction-specific fields

// frontend/src/components/canon/MagicRuleForm.tsx
// Similar structure with magic-specific fields

// frontend/src/components/canon/ItemForm.tsx
// Similar structure with item-specific fields

// frontend/src/components/canon/EventForm.tsx
// Similar structure with event-specific fields

// Update canon/page.tsx to include all tabs
```

---

*Note: Due to length, I'll summarize the remaining weeks...*

## Week 3: Performance & Infrastructure ⚡

- Redis caching layer
- Connection pooling fixes
- Background job system (Celery)
- N+1 query optimization
- Database indexing
- Staging environment setup
- CI/CD pipeline (GitHub Actions)

## Week 4: Testing & Monitoring 🧪

- Unit tests (pytest) - 80% coverage target
- Integration tests (API routes)
- E2E tests (Playwright)
- Sentry error tracking
- DataDog APM
- Load testing (Locust)

## Week 5-6: Advanced AI Features 🤖

- Character Voice Fingerprinting
- Consequence Simulation Engine
- Style consistency checks
- Intelligent canon suggestions

## Week 7-8: Collaboration & Polish ✨

- Real-time features (WebSocket)
- Collaboration (invites, permissions)
- Advanced search
- Analytics dashboard
- Mobile optimization

---

## Installation Checklist per Week

### Week 1 Dependencies:
```bash
# Backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# Frontend
npm install zustand zustand/middleware
```

### Week 2 Dependencies:
```bash
# Backend
pip install python-docx ebooklib WeasyPrint

# Frontend
# No new dependencies
```

### Week 3 Dependencies:
```bash
# Backend
pip install redis celery flower

# Infrastructure
docker-compose.yml updates for Redis/Celery
```

---

**Total Timeline:** 8 weeks to production-ready v1.0

**Next Steps:** Start with Week 1, Day 1 - Authentication system!
