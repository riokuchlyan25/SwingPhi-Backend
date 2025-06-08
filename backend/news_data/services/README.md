# News Data Service Architecture

This document explains the reorganized service architecture for the news_data app, following clean architecture principles.

## Architecture Overview

The news_data app has been reorganized to follow a service-oriented architecture pattern where:

- **Views**: Pure handlers that delegate to services
- **Services**: Business logic, request processing, and external API calls
- **Clear separation**: UI logic separated from business logic

## File Structure

```
news_data/
├── services/
│   ├── __init__.py
│   ├── news_service.py          # Core business logic
│   └── README.md                # This file
├── views.py                     # Pure handlers only
├── urls.py                      # URL routing
├── config.py                    # Configuration
└── templates/                   # HTML templates
```

## Service Layer (`news_service.py`)

### Core Functions:

#### `get_news_headlines(request)`
- **Purpose**: Main service function for handling news API requests
- **Responsibilities**:
  - HTTP method validation
  - Request parsing (JSON/form data)
  - Input validation
  - NewsAPI integration
  - Error handling
- **Returns**: JsonResponse with articles or error

#### `get_news_headlines_template_context()`
- **Purpose**: Generate context for headlines template
- **Returns**: Dictionary with template context

#### `get_news_test_dashboard_context()`
- **Purpose**: Generate context for test dashboard template
- **Returns**: Dictionary with template context

#### `get_news_test_index_context()`
- **Purpose**: Generate context for test index template
- **Returns**: Dictionary with template context

#### `_extract_query_from_request(request)` (Private)
- **Purpose**: Extract query parameter from request
- **Handles**: Both JSON and form data
- **Returns**: Cleaned query string

#### `get_top_headlines(query)` (Legacy)
- **Purpose**: Backward compatibility
- **Direct**: NewsAPI integration with query string

## View Layer (`views.py`)

### Pure Handlers:

#### `news_api_view(request)`
```python
@csrf_exempt
def news_api_view(request):
    return get_news_headlines(request)
```

#### `news_headlines_template(request)`
```python
def news_headlines_template(request):
    context = get_news_headlines_template_context()
    return render(request, 'news_data/news_headlines.html', context)
```

#### `news_test_dashboard(request)`
```python
def news_test_dashboard(request):
    context = get_news_test_dashboard_context()
    return render(request, 'news_data/news_test_dashboard.html', context)
```

#### `news_test_index(request)`
```python
def news_test_index(request):
    context = get_news_test_index_context()
    return render(request, 'news_data/news_test_index.html', context)
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- Views handle HTTP requests/responses only
- Services handle business logic only
- Templates handle presentation only

### 2. **Testability**
- Services can be unit tested independently
- Business logic isolated from Django framework
- Mock-friendly design

### 3. **Reusability**
- Services can be called from multiple views
- Business logic can be shared across endpoints
- Easy to add new interfaces (CLI, API versions, etc.)

### 4. **Maintainability**
- Clear responsibility boundaries
- Easy to modify business logic without touching views
- Consistent error handling patterns

### 5. **Scalability**
- Services can be moved to separate modules/packages
- Easy to implement caching at service level
- Clear API contracts between layers

## Usage Examples

### API Endpoint Usage:
```bash
curl -X POST "http://localhost:8000/news_data/headlines/" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tesla"}'
```

### Template Views:
- `/news_data/` - Test suite index
- `/news_data/headlines/template/` - Basic testing interface
- `/news_data/test-dashboard/` - Advanced testing dashboard

## Error Handling

The service layer provides comprehensive error handling:

- **HTTP Method Validation**: Only POST allowed for API endpoints
- **Input Validation**: Required parameters checked
- **API Error Handling**: NewsAPI exceptions caught and formatted
- **Request Parsing**: Handles both JSON and form data gracefully

## Future Enhancements

This architecture makes it easy to add:

- **Caching**: Add Redis caching at service level
- **Rate Limiting**: Implement in service layer
- **Authentication**: Add auth checks in services
- **Logging**: Centralized logging in services
- **Metrics**: Performance monitoring in services
- **New Endpoints**: Just add new handlers that call services 