from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import TypeVar, Generic, List, Optional, Type
from ..database import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def create(self, obj_in) -> T:
        """Создать новый объект"""
        db_obj = self.model(**obj_in.dict())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить объект по ID"""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить все объекты с pagination"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update(self, db_obj: T, obj_in) -> T:
        """Обновить объект"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, db_obj: T) -> None:
        """Удалить объект"""
        await self.session.delete(db_obj)
        await self.session.commit()
    
    async def delete_by_id(self, id: int) -> bool:
        """Удалить объект по ID"""
        obj = await self.get_by_id(id)
        if obj:
            await self.delete(obj)
            return True
        return False
    
    async def count(self) -> int:
        """Получить количество объектов"""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar()
