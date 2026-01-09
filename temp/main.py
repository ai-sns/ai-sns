from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import SecuritySchemeType
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, insert
from pydantic import BaseModel, EmailStr, validator
from typing import List, Dict, Optional, Annotated
from datetime import datetime, timedelta
from io import BytesIO
import os
import random
import string
import uuid
import math
from PIL import Image, ImageDraw, ImageFont
from captcha.image import ImageCaptcha
from jose import jwt, JWTError

# FastAPI实例，配置文档路径
app = FastAPI(
    docs_url="/api/docs",  # 强制指定文档路径
    openapi_url="/api/openapi.json"  # 同步修改OpenAPI schema路径
)

# 数据库连接配置（使用peer认证）
DB_PASSWORD = os.getenv("DB_PASSWORD", "A@dt0734")
DATABASE_URL = f"postgresql+asyncpg://postgres:{DB_PASSWORD}@/gis_db?host=/var/run/postgresql"

# 创建异步数据库引擎
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 内存存储验证码信息（生产环境建议使用Redis）
captcha_store: Dict[str, dict] = {}
CAPTCHA_EXPIRE_SECONDS = 300  # 5分钟有效期

# 头像保存路径
AVATAR_UPLOAD_PATH = "./uploads/avatars/"

# 确保上传目录存在
os.makedirs(AVATAR_UPLOAD_PATH, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "6d4e282ec81cEb7df8ea21A8554253981e79c7K426ae53e681fa3e4b6U576dcc")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")


# 响应模型
class DistanceResult(BaseModel):
    place1: str
    place2: str
    distance_meters: float


# 数据库会话依赖项
async def get_db():
    async with async_session() as session:
        yield session


@app.get("/api/")
def read_root():
    return {"Hello888": "World888"}


@app.get("/api/distance", response_model=List[DistanceResult])
async def calculate_distance(
        place1: str = 'Home',
        place2: str = 'Work',
        db: AsyncSession = Depends(get_db)
):
    """
    计算两个地点之间的地理距离（米）
    默认查询Home和Work的地点组合
    """
    query = text("""
    SELECT 
        a.name AS place1,
        b.name AS place2,
        ST_Distance(a.geom::geography, b.geom::geography) AS distance_meters
    FROM places a, places b
    WHERE a.name = :name1 AND b.name = :name2;
    """)

    try:
        result = await db.execute(query, {'name1': place1, 'name2': place2})
        return [dict(row) for row in result.mappings()]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


def generate_captcha_code(length: int = 6) -> str:
    """生成一个随机的字母数字验证码文本"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_captcha_image(captcha_code: str) -> BytesIO:
    """生成验证码图像并返回图像的字节流"""
    image = ImageCaptcha()
    data = image.generate(captcha_code)
    return data


@app.get("/api/captcha/")
async def get_captcha():
    captcha_code = generate_captcha_code()
    captcha_image_data = generate_captcha_image(captcha_code)
    print("captcha_code", captcha_code)
    # 将验证码文本存储在内存中
    captcha_id = uuid.uuid4().hex
    captcha_store[captcha_id] = {
        "code": captcha_code,
        "expire_at": datetime.now() + timedelta(seconds=CAPTCHA_EXPIRE_SECONDS)
    }

    return StreamingResponse(captcha_image_data, media_type="image/png", headers={"X-Captcha-ID": captcha_id})


class UserRegisterRequest(BaseModel):
    nation_id: str
    password: str
    account: str
    longitude: float
    latitude: float
    captcha_id: str
    captcha_code: str
    nick_name: str
    avatar: str
    avatar_3d: str
    profile: str
    sns_url: str
    status: int

    @validator('password')
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('account')
    def account_validation(cls, v):
        if not v:
            raise ValueError('Account cannot be empty')
        return v


def generate_random_nation_id() -> str:
    """生成一个以AI开头的20位随机字符串"""
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    return f"AI000000{random_suffix}"


@app.post("/api/register/")
async def register_user(
        nation_id: Annotated[str, Form()],
        password: Annotated[str, Form()],
        account: Annotated[str, Form()],
        longitude: Annotated[float, Form()],
        latitude: Annotated[float, Form()],
        captcha_id: Annotated[str, Form()],
        captcha_code: Annotated[str, Form()],
        nick_name: Annotated[str, Form()],
        avatar: Annotated[str, Form()],
        avatar_3d: Annotated[str, Form()],
        profile: Annotated[str, Form()],
        sns_url: Annotated[str, Form()],
        status: Annotated[int, Form()],
        avatar_file: UploadFile = File(...),  # 接收上传的头像文件
        db: AsyncSession = Depends(get_db)
):
    """
    用户注册接口，包含验证码验证和用户信息存储
    """
    captcha_info = captcha_store.get(captcha_id)
    if not captcha_info:
        raise HTTPException(status_code=400, detail="Invalid captcha ID")

    if datetime.now() > captcha_info["expire_at"]:
        del captcha_store[captcha_id]
        raise HTTPException(status_code=401, detail="Captcha expired")

    if captcha_code.upper() != captcha_info["code"]:
        raise HTTPException(status_code=402, detail="Invalid captcha code")

    del captcha_store[captcha_id]

    if not nation_id:
        nation_id = generate_random_nation_id()

    existing_user = await db.execute(
        text("SELECT 1 FROM users WHERE nation_id = :nation_id OR account = :account"),
        {"nation_id": nation_id, "account": account}
    )

    user_exist = existing_user.scalar()

    try:
        avatar_filename = f"{account.replace('@', '_').replace('.', '_')}.png"
        avatar_file_path = os.path.join(AVATAR_UPLOAD_PATH, avatar_filename)

        with open(avatar_file_path, "wb") as f:
            f.write(await avatar_file.read())

        lon_str = str(longitude)
        lat_str = str(latitude)
        wkt_point = f"POINT({lon_str} {lat_str})"

        if user_exist:
            sql = text("""
            UPDATE users SET 
                password = :password,
                location = ST_GeomFromText(:wkt_point, 4326),
                nick_name = :nick_name,
                avatar = :avatar,
                status = 1,
                create_time = NOW() 
            WHERE nation_id = :nation_id
            """)
            await db.execute(sql, {
                "nation_id": nation_id,
                "password": hash_password(password),
                "wkt_point": wkt_point,
                "nick_name": nick_name,
                "avatar": avatar
            })
        else:
            sql = text("""
            INSERT INTO users (
                nation_id, 
                password, 
                account, 
                location, 
                nick_name, 
                avatar, 
                status, 
                create_time
            ) VALUES (
                :nation_id,
                :password,
                :account,
                ST_GeomFromText(:wkt_point, 4326),
                :nick_name,
                :avatar,
                1,
                NOW()
            )
            """)
            await db.execute(sql, {
                "nation_id": nation_id,
                "password": hash_password(password),
                "account": account,
                "wkt_point": wkt_point,
                "nick_name": nick_name,
                "avatar": avatar
            })

        await db.commit()

        return JSONResponse(
            status_code=201 if not user_exist else 200,
            content={"message": "User registered successfully" if not user_exist else "User updated successfully", "nation_id": nation_id}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


def hash_password(password: str) -> str:
    """简单的密码哈希演示函数，实际应用中应该使用bcrypt或类似库"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


class NearbyUser(BaseModel):
    nation_id: str
    account: str
    nick_name: str
    avatar: str
    distance_meters: float
    location: List[float]  # 新增location字段


# 新增：生成访问令牌和刷新令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 新增：登录用户并返回令牌
@app.post("/api/login/")
async def login(username: str = Form("AI000000BGRWDKCEGZNOBN4ATA9A"),
                password: str = Form("securePassword123!"),
                db: AsyncSession = Depends(get_db)
                ):
    # 验证用户凭证
    nation_id = username
    result = await db.execute(
        text("SELECT password FROM users WHERE nation_id = :nation_id"),
        {"nation_id": nation_id}
    )
    user = result.scalar()

    if not user or hash_password(password) != user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": nation_id}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": nation_id}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/api/refresh-token/")
async def refresh_access_token(refresh_token: str = Form(...)):
    """
    使用刷新令牌获取新的访问令牌
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)

    return {"access_token": access_token}


@app.post("/api/upload_avatar/")
async def upload_avatar(
        nation_id: Annotated[str, Form()],
        avatar_file: UploadFile = File(...),  # 接收上传的头像文件
        db: AsyncSession = Depends(get_db)
):
    """
    用户头像上传接口
    """
    try:
        # 生成头像文件名
        avatar_filename = f"{nation_id}_avatar.png"
        avatar_file_path = os.path.join(AVATAR_UPLOAD_PATH, avatar_filename)

        # 保存上传的头像文件
        with open(avatar_file_path, "wb") as f:
            f.write(await avatar_file.read())

        # 更新数据库中用户的头像信息
        sql = text("""
        UPDATE users SET 
            avatar = :avatar
        WHERE nation_id = :nation_id
        """)
        await db.execute(sql, {
            "nation_id": nation_id,
            "avatar": avatar_filename
        })
        
        await db.commit()

        return JSONResponse(
            status_code=200,
            content={"message": "Avatar uploaded successfully", "avatar": avatar_filename}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Avatar upload failed: {str(e)}")


@app.post("/api/update-location/")
async def update_location(
        nation_id: str = Form(...),
        password: str = Form(...),
        longitude: float = Form(...),
        latitude: float = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """
    更新用户的地理位置（location 字段）
    - 使用 nation_id + password 验证身份
    - 改为 POST 调用
    """
    hashed_pwd = hash_password(password)
    wkt_point = f"POINT({longitude} {latitude})"

    result = await db.execute(
        text("""UPDATE users 
                SET location = ST_GeomFromText(:wkt_point, 4326) 
                WHERE nation_id = :nation_id 
                AND password = :hashed_pwd"""),
        {
            "wkt_point": wkt_point,
            "nation_id": nation_id,
            "hashed_pwd": hashed_pwd
        }
    )

    if result.rowcount == 0:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await db.commit()
    return {"message": "Location updated successfully"}


@app.post("/api/update-profession/")
async def update_profession(
        nation_id: str = Form(...),
        password: str = Form(...),
        profession: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """
    更新用户的职业（profession 字段）
    - 使用 nation_id + password 验证身份
    - 改为 POST 调用
    """
    hashed_pwd = hash_password(password)

    result = await db.execute(
        text("""UPDATE users 
                SET profession = :profession 
                WHERE nation_id = :nation_id 
                AND password = :hashed_pwd"""),
        {
            "profession": profession,
            "nation_id": nation_id,
            "hashed_pwd": hashed_pwd
        }
    )

    if result.rowcount == 0:
        raise HTTPException(status_code=401, detail="Invalid credentials or no changes made")

    await db.commit()
    return {"message": "Profession updated successfully"}


# 新增：获取附近用户（包含JWT验证）
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username


class UserResponse(BaseModel):
    nation_id: str
    account: str
    location: List[float]
    nick_name: str
    avatar: str
    avatar_3d: str
    profile: str
    sns_url: str


async def validate_geo_coordinates(longitude: float, latitude: float):
    """验证地理坐标是否有效"""
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude value, must be between -180 and 180")
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude value, must be between -90 and 90")


async def execute_nearby_users_query(db: AsyncSession, longitude: float, latitude: float, max_distance: int, limit: int):
    """执行附近用户查询并返回结果"""
    query = text("""
    SELECT 
        nation_id,
        account,
        nick_name,
        avatar,
        avatar_3d,
        profile,
        sns_url,
        ST_X(location::geometry) AS longitude,
        ST_Y(location::geometry) AS latitude,
        ST_Distance(
            ST_Transform(location::geometry, 3857),
            ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 3857)
        ) AS distance_meters
    FROM users
    WHERE status = 1 
      AND ST_DWithin(
        ST_Transform(location::geometry, 3857),
        ST_Transform(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 3857),
        :max_dist
      )
    ORDER BY distance_meters ASC
    LIMIT :limit
    """)

    result = await db.execute(query, {
        'lon': longitude,
        'lat': latitude,
        'max_dist': max_distance,
        'limit': limit
    })

    return [{
        "nation_id": row.nation_id,
        "account": row.account,
        "location": [row.longitude, row.latitude],
        "nick_name": row.nick_name,
        "avatar": row.avatar,
        "avatar_3d": row.avatar_3d,
        "profile": row.profile,
        "sns_url": row.sns_url
    } for row in result]


@app.get("/api/get_nearest_people/", response_model=List[UserResponse])
async def get_nearby_users(
        longitude: float = 116.27882,
        latitude: float = 39.71164,
        max_distance: int = 5000,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定经纬度附近的人员列表
    - longitude: 经度，范围-180到180
    - latitude: 纬度，范围-90到90
    - max_distance: 最大距离(米)，必须为正数
    - limit: 返回结果最大数量
    """
    await validate_geo_coordinates(longitude, latitude)
    if max_distance <= 0:
        raise HTTPException(status_code=400, detail="Max distance must be positive")
    try:
        return await execute_nearby_users_query(db, longitude, latitude, max_distance, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/get_nearest_people_v2/", response_model=List[UserResponse])
async def get_nearby_users_v2(
        longitude: float = 116.27882,
        latitude: float = 39.71164,
        max_distance: int = 5000,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    """
    获取指定经纬度附近的人员列表（需要身份验证）
    - 参数同上
    """
    await get_current_user(token)  # 验证token
    await validate_geo_coordinates(longitude, latitude)
    if max_distance <= 0:
        raise HTTPException(status_code=400, detail="Max distance must be positive")
    try:
        return await execute_nearby_users_query(db, longitude, latitude, max_distance, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/api/update-user/")
async def update_user_post(
        nation_id: str = Form("AI000000BGRWDKCEGZNOBN4ATA9A"),
        password: str = Form("securePassword123!"),
        account: Optional[str] = Form(None),
        nick_name: Optional[str] = Form(None),
        avatar_3d: Optional[str] = Form(None),
        profile: Optional[str] = Form(None),
        sns_url: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db)
):
    # 必须字段参数验证和处理
    hashed_pwd = hash_password(password)

    # 构建动态SQL参数和条件
    update_fields = {}
    if account is not None:
        update_fields["account"] = account
    if nick_name is not None:
        update_fields["nick_name"] = nick_name
    if avatar_3d is not None:
        update_fields["avatar_3d"] = avatar_3d
    if profile is not None:
        update_fields["profile"] = profile
    if sns_url is not None:
        update_fields["sns_url"] = sns_url

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    # 构建动态SQL的SET部分
    set_clause = ", ".join(f"{key} = :{key}" for key in update_fields.keys())

    # 执行带条件的动态UPDATE语句
    query = text(f"""UPDATE users 
                     SET {set_clause} 
                     WHERE nation_id = :nation_id 
                     AND password = :hashed_pwd""")
    params = {**update_fields, "nation_id": nation_id, "hashed_pwd": hashed_pwd}

    result = await db.execute(query, params)

    # 检查受影响行数
    if result.rowcount == 0:
        raise HTTPException(status_code=401, detail="Invalid credentials or no changes made")

    await db.commit()
    return {"message": "User information updated successfully"}


@app.post("/api/change-password/")
async def change_password(
        nation_id: str = Form(...),
        old_password: str = Form(...),
        new_password: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """
    修改用户密码接口
    - nation_id: 用户ID
    - old_password: 旧密码
    - new_password: 新密码
    """
    # 验证新密码强度
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
    
    # 验证旧密码是否正确
    old_hashed_pwd = hash_password(old_password)
    
    # 查询用户并验证旧密码
    result = await db.execute(
        text("SELECT 1 FROM users WHERE nation_id = :nation_id AND password = :hashed_pwd"),
        {"nation_id": nation_id, "hashed_pwd": old_hashed_pwd}
    )
    
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid nation_id or old password")
    
    # 更新密码
    new_hashed_pwd = hash_password(new_password)
    await db.execute(
        text("UPDATE users SET password = :new_hashed_pwd WHERE nation_id = :nation_id"),
        {"new_hashed_pwd": new_hashed_pwd, "nation_id": nation_id}
    )
    
    await db.commit()
    
    return {"message": "Password changed successfully"}


@app.post("/api/get_service_list/")
async def get_service_list(
        lng: Annotated[float, Form()],
        lat: Annotated[float, Form()],
        db: AsyncSession = Depends(get_db)
):
    """
    从 services 表获取服务列表
    返回 JSON 格式与原先固定数据一致
    """
    try:
        query = text("""
            SELECT 
                service_id AS id,
                name,
                description,
                place,
                ST_X(position::geometry) AS lng,
                ST_Y(position::geometry) AS lat,
                type,
                address,
                method,
                parameter
            FROM services
            ORDER BY id
        """)
        result = await db.execute(query)
        content = []
        for row in result.mappings():
            param = row["parameter"]
            # JSONB字段直接返回JSON对象，如果是字符串"None"，保持一致
            if isinstance(param, str) and param == "None":
                param_value = "None"
            else:
                param_value = param
            content.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "place": row["place"],
                "lng": row["lng"],
                "lat": row["lat"],
                "type": row["type"],
                "address": row["address"],
                "method": row["method"],
                "parameter": param_value
            })
        return JSONResponse(status_code=200, content=content)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Get service list failed: {str(e)}")


@app.post("/api/get_people_list/")
async def get_people_list(
        lng: Annotated[float, Form()],
        lat: Annotated[float, Form()],
        db: AsyncSession = Depends(get_db)
):
    """
    从 users 表获取用户列表
    返回 JSON 格式与原先固定数据一致
    """
    try:
        query = text("""
            SELECT 
                nation_id,
                account,
                nick_name,
                avatar,
                avatar_3d,
                profile,
                sns_url,
                profession,
                ST_X(location::geometry) AS lng,
                ST_Y(location::geometry) AS lat
            FROM users
            WHERE status = 1
            ORDER BY create_time DESC
        """)
        result = await db.execute(query)
        content = []
        for row in result.mappings():
            content.append({
                "nation_id": row["nation_id"],
                "account": row["account"],
                "location": [row["lng"], row["lat"]],
                "nick_name": row["nick_name"],
                "avatar": row["avatar"],
                "avatar_3d": row["avatar_3d"],
                "profile": row["profile"],
                "sns_url": row["sns_url"],
                "profession": row["profession"]
            })
        return JSONResponse(status_code=200, content=content)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Get people list failed: {str(e)}")


@app.post("/api/get_place_list/")
async def get_place_list(
        lng: Annotated[float, Form()],
        lat: Annotated[float, Form()],
        db: AsyncSession = Depends(get_db)
):
    """
    从 places 表获取地点列表
    返回 JSON 格式与原先固定数据一致
    """
    try:
        query = text("""
            SELECT 
                place_id,
                place_name,
                ST_X(place_position::geometry) AS lng,
                ST_Y(place_position::geometry) AS lat,
                description
            FROM places
            ORDER BY id
        """)
        result = await db.execute(query)
        content = []
        for row in result.mappings():
            content.append({
                "place_id": row["place_id"],
                "place_name": row["place_name"],
                "place_position": [row["lng"], row["lat"]],
                "description": row["description"]
            })
        return JSONResponse(status_code=200, content=content)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Get place list failed: {str(e)}")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
