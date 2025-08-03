from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# Enums for better type safety and data integrity
class UserRole(str, Enum):
    ADMINISTRATOR = "Administrator"
    TEKNISI = "Teknisi"
    USER = "User"


class MaintenanceStatus(str, Enum):
    SELESAI = "Selesai"
    TERTUNDA = "Tertunda"
    DALAM_PROSES = "Dalam Proses"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=100, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    nama_lengkap: str = Field(max_length=200)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    maintenance_records: List["MaintenanceRecord"] = Relationship(back_populates="teknisi")


class SwitchDevice(SQLModel, table=True):
    __tablename__ = "switch_devices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nama_perangkat: str = Field(max_length=200, index=True)
    lokasi_perangkat: str = Field(max_length=500)  # Deskripsi teks lokasi
    model: str = Field(max_length=100)
    nomor_seri: str = Field(max_length=100, unique=True, index=True)
    tanggal_implementasi: date
    ip_address: str = Field(max_length=45)  # IPv4 or IPv6

    # Koordinat geografis untuk Google Maps
    latitude: Decimal = Field(decimal_places=8, max_digits=11)  # -90.00000000 to 90.00000000
    longitude: Decimal = Field(decimal_places=8, max_digits=12)  # -180.00000000 to 180.00000000

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    maintenance_records: List["MaintenanceRecord"] = Relationship(back_populates="switch_device")


class MaintenanceRecord(SQLModel, table=True):
    __tablename__ = "maintenance_records"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    switch_device_id: int = Field(foreign_key="switch_devices.id", index=True)
    teknisi_id: int = Field(foreign_key="users.id", index=True)

    tanggal_maintenance: date = Field(index=True)
    nama_teknisi: str = Field(max_length=200)  # Redundant with teknisi relationship for easier queries
    deskripsi_pekerjaan: str = Field(max_length=2000)
    status: MaintenanceStatus = Field(default=MaintenanceStatus.TERTUNDA, index=True)

    # Additional maintenance details
    jenis_maintenance: str = Field(max_length=50, default="PM")  # PM (Preventive) or CM (Corrective)
    catatan_tambahan: str = Field(default="", max_length=1000)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    switch_device: SwitchDevice = Relationship(back_populates="maintenance_records")
    teknisi: User = Relationship(back_populates="maintenance_records")


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=100)
    email: str = Field(max_length=255)
    nama_lengkap: str = Field(max_length=200)
    role: UserRole = Field(default=UserRole.USER)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    nama_lengkap: Optional[str] = Field(default=None, max_length=200)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class SwitchDeviceCreate(SQLModel, table=False):
    nama_perangkat: str = Field(max_length=200)
    lokasi_perangkat: str = Field(max_length=500)
    model: str = Field(max_length=100)
    nomor_seri: str = Field(max_length=100)
    tanggal_implementasi: date
    ip_address: str = Field(max_length=45)
    latitude: Decimal = Field(decimal_places=8, max_digits=11)
    longitude: Decimal = Field(decimal_places=8, max_digits=12)


class SwitchDeviceUpdate(SQLModel, table=False):
    nama_perangkat: Optional[str] = Field(default=None, max_length=200)
    lokasi_perangkat: Optional[str] = Field(default=None, max_length=500)
    model: Optional[str] = Field(default=None, max_length=100)
    nomor_seri: Optional[str] = Field(default=None, max_length=100)
    tanggal_implementasi: Optional[date] = Field(default=None)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    latitude: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=11)
    longitude: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=12)


class MaintenanceRecordCreate(SQLModel, table=False):
    switch_device_id: int
    teknisi_id: int
    tanggal_maintenance: date
    nama_teknisi: str = Field(max_length=200)
    deskripsi_pekerjaan: str = Field(max_length=2000)
    status: MaintenanceStatus = Field(default=MaintenanceStatus.TERTUNDA)
    jenis_maintenance: str = Field(max_length=50, default="PM")
    catatan_tambahan: str = Field(default="", max_length=1000)


class MaintenanceRecordUpdate(SQLModel, table=False):
    tanggal_maintenance: Optional[date] = Field(default=None)
    nama_teknisi: Optional[str] = Field(default=None, max_length=200)
    deskripsi_pekerjaan: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[MaintenanceStatus] = Field(default=None)
    jenis_maintenance: Optional[str] = Field(default=None, max_length=50)
    catatan_tambahan: Optional[str] = Field(default=None, max_length=1000)


# Response schemas for API endpoints
class SwitchDeviceResponse(SQLModel, table=False):
    id: int
    nama_perangkat: str
    lokasi_perangkat: str
    model: str
    nomor_seri: str
    tanggal_implementasi: str  # Will be converted to ISO format
    ip_address: str
    latitude: Decimal
    longitude: Decimal
    google_maps_url: str  # Computed field
    created_at: str  # Will be converted to ISO format
    updated_at: str  # Will be converted to ISO format


class MaintenanceRecordResponse(SQLModel, table=False):
    id: int
    switch_device_id: int
    teknisi_id: int
    tanggal_maintenance: str  # Will be converted to ISO format
    nama_teknisi: str
    deskripsi_pekerjaan: str
    status: MaintenanceStatus
    jenis_maintenance: str
    catatan_tambahan: str
    created_at: str  # Will be converted to ISO format
    updated_at: str  # Will be converted to ISO format

    # Related data
    switch_device: Optional[SwitchDeviceResponse] = None
    teknisi: Optional["UserResponse"] = None


class UserResponse(SQLModel, table=False):
    id: int
    username: str
    email: str
    nama_lengkap: str
    role: UserRole
    is_active: bool
    created_at: str  # Will be converted to ISO format
    updated_at: str  # Will be converted to ISO format


# Dashboard/Statistics schemas
class MaintenanceStats(SQLModel, table=False):
    total_maintenance: int
    selesai: int
    tertunda: int
    dalam_proses: int
    maintenance_bulan_ini: int


class SwitchStats(SQLModel, table=False):
    total_switches: int
    switches_dengan_maintenance_tertunda: int
    switches_tanpa_maintenance: int
    total_lokasi_unik: int
