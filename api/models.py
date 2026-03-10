# Упрощенная версия models.py без Pydantic
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class Price(BaseModel):
    """Модель цены товара."""
    current: Union[int, float]
    old: Optional[Union[int, float]] = None
    discount: Optional[int] = None


class Product(BaseModel):
    """Модель товара (книги)."""
    id: str = Field(alias='productId')
    title: str
    author: Optional[str] = None
    price: Price
    publisher: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None
    in_stock: bool = Field(alias='inStock', default=False)
    image_url: Optional[str] = Field(alias='imageUrl', default=None)

    class Config:
        allow_population_by_field_name = True  # Для Pydantic V1


class SearchResponse(BaseModel):
    """Модель ответа на поисковый запрос."""
    total: int
    page: int
    limit: int
    items: List[Product]
    facets: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True


class AuthorSearchResponse(BaseModel):
    """
    Модель ответа при поиске по автору.
    Используется в тесте test_search_by_russian_author
    """
    author: str
    total_books: int = Field(alias='totalBooks')
    books: List[Product]

    class Config:
        allow_population_by_field_name = True


class AvailabilityInfo(BaseModel):
    """Модель информации о наличии книги в магазине."""
    store_id: str = Field(alias='storeId')
    store_name: str = Field(alias='storeName')
    quantity: int
    address: str

    class Config:
        allow_population_by_field_name = True


class AvailabilityResponse(BaseModel):
    """Модель ответа о наличии книги."""
    stores: List[AvailabilityInfo]
    total_stores: int = Field(alias='totalStores', default=0)

    class Config:
        allow_population_by_field_name = True


class ErrorResponse(BaseModel):
    """Модель ответа с ошибкой."""
    error: Optional[str] = None
    message: Optional[str] = None
    status_code: Optional[int] = Field(alias='statusCode', default=None)

    class Config:
        allow_population_by_field_name = True