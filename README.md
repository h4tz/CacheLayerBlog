
# 🧠 Project_01_CacheLayerBlog

A Django blog project focused on implementing **caching strategies** using `cache_page`, `django-redis`, and Redis backend.

## 🚀 Project Overview

This project demonstrates how to implement effective caching in a Django app to boost performance and reduce unnecessary database hits.

**Key Features:**

- Blog app with post list and detail views
- Fake post data generated with `Faker`
- Homepage cached for 15 seconds
- Individual post pages cached separately using `@cache_page`
- Redis used as caching backend via `django-redis`
- REST Client used for API testing
- PostgreSQL as the database

---

## 🧩 Concepts Covered

| Concept            | Description |
|--------------------|-------------|
| `@cache_page`      | Django's decorator to cache entire view responses |
| Template Fragment  | Option to cache parts of a template using `{% cache %}` |
| Redis              | In-memory cache layer to store view responses |
| `django-redis`     | Django cache backend using Redis |
| `Faker`            | Python library to generate fake blog post content |
| REST Client        | Tool for testing API endpoints easily |
| PostgreSQL         | Configured as the main database engine |

---

## 🛠️ Setup & Technologies

- **Backend:** Django
- **Database:** PostgreSQL
- **Caching Layer:** Redis (`django-redis`)
- **Testing Tools:** REST Client (Thunder Client/Postman)
- **Data Generator:** `Faker` for mock blog posts

---

## 🏗️ Implementation Details

### 1. 🧪 Fake Data with `Faker`

```bash
pip install faker
```

Used to generate 10 blog posts with realistic content.

### 2. 🧰 Caching with `cache_page`

- Homepage view (`/blog/`) is cached for **15 seconds**
- Individual post pages (`/blog/<slug>/`) cached separately for **5 minutes**

### 3. 🧠 Redis Integration

**Installed Redis** on local machine and configured Django to use it via:

```bash
pip install django-redis
```

In `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 4. 🧪 REST Client

Used REST Client to test the API endpoints:
- `/api/posts/` → List of all blog posts
- `/api/posts/<slug>/` → Individual post detail

---

## ✅ What I Learned

- How to implement and test **view-level caching** with `@cache_page`
- How Redis works behind the scenes for fast response delivery
- How to use **`Faker`** to auto-generate realistic mock data
- The difference between template caching and view caching
- How to connect Django to **PostgreSQL**
- Debugging cache issues (e.g., not seeing updates until cache expires)
- Inspecting Redis using `redis-cli`
- Using tools like REST Client to rapidly test API endpoints

---

## 🧱 Project Structure Highlights

```
Project_01_CacheLayerBlog/
├── blog/
│   ├── models.py
│   ├── views.py  ← cache_page used here
│   ├── urls.py
│   └── templates/
│       ├── post_list.html
│       └── post_detail.html
├── static/
│   ├── css/
│   └── js/
├── manage.py
├── requirements.txt
└── README.md
```

---

## ❌ Challenges Faced

- Redis wasn't caching views until I confirmed the view was decorated correctly
- Static files weren't loading (fixed via correct `STATICFILES_DIRS`)
- API wasn't responding due to a trailing slash (`/api/posts/` vs `/api/posts`)
- Debugging view rendering to confirm if cache was being used
- Learning how to inspect Redis keys using `redis-cli`

---

## 📦 Requirements

```txt
Django
django-redis
psycopg2
Faker
```

Install with:

```bash
pip install -r requirements.txt
```

---

## 📌 Conclusion

This project gave me hands-on experience with Django caching and Redis integration. It helped me understand how to reduce server load and optimize performance by serving cached views. Caching is a powerful concept and will definitely be a part of my future production-grade apps.

---
