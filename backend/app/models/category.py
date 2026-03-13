from sqlmodel import SQLModel, Field

class CategoryBase(SQLModel):
    name: str = Field(index=True)
    is_active: bool = Field(default=True)

class Category(CategoryBase, table=True):
    __tablename__ = "m_category"
    id: int | None = Field(default=None, primary_key=True)
