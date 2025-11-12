import json
from django.http.response import JsonResponse
from django.http import FileResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from library.services.books_catalog_service import BooksCatalogService  # Import inside the method
from library.services.user_profile_service import UserProfileService


class LibraryDashboardTitlesAPIView(APIView):
    """
    Prototype: Handles the initial display of the dashboard/titles list.
    Pre-conditions: GET request. User is authenticated. Optional query parameters for sorting/searching.
    Post-conditions: Returns an HTTP Response (200 OK) with the serialized list of books.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        booksCatalogService = BooksCatalogService()
        titles = booksCatalogService.get_dashboard_titles(None, {}, {}) #TODO: Implement pagination and filtering
        try:
            response = JsonResponse({'titles': list(titles)})
        except Exception as e:
            response = JsonResponse({'An error occurred': str(e)}, status=500)
        return response

class LibraryDashboardTitlesCoversAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> FileResponse | JsonResponse:
        import os

        cover_path = request.GET.get('cover_path', None)
        if not cover_path:
            return JsonResponse({'error': 'Missing required parameter: cover_path'}, status=400)

        try:
            if os.path.isfile(cover_path):
                response = FileResponse(open(cover_path, 'rb'), content_type='image/jpeg')
            else:
                response = JsonResponse({'error': f'Cover not found: {cover_path}'}, status=404)
        except Exception as e:
            response = JsonResponse({'An error occurred': str(e)}, status=500)
        return response

class LibraryTitlesBooksAPIView(APIView):
    """
    Prototype: Retrieves a list of books belonging to a specific title.
    Pre-conditions: GET request with 'title_name' in the URL.
    Post-conditions: Returns HTTP Response (200 OK) with a list of books, or 404 Not Found.
    """

    permission_classes = [IsAuthenticated]
    def get(self, request: Request, title_name: str, *args, **kwargs) -> Response | JsonResponse:
        from library.serializers import BookListSerializer

        booksCatalogService = BooksCatalogService()
        books = booksCatalogService.get_books_by_title_name(title_name)
        serialized_books = BookListSerializer(books, many=True)
        try:
            serialized_books.data
            response = Response(serialized_books.data, status=200)
        except Exception as e:
            response = JsonResponse({'An error occurred': str(e)}, status=500)
        return response

class LibraryRefreshAPIView(APIView):
    """
    Prototype: Triggers the book catalog refresh process.
    Pre-conditions: POST request. User is authenticated. Optionally, 'scan_directory_path' in the body.
    Post-conditions: Returns HTTP Response (202 Accepted) if scan is launched. 400 Bad Request if validation fails.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        booksCatalogService = BooksCatalogService()
        booksCatalogService.initiate_library_scan(None, request.user.id)
        return Response({"content_type": "application/json", "message": "Scan launched successfully, please wait for the scan to complete."}, status=202)

    def get(self, request: Request, *args, **kwargs) -> Response:
        return Response({"content_type": "application/json", "message": "Scan launched successfully"}, status=202)

class BookDetailAPIView:
    '''
    Prototype: Handles the request to display the details of a specific book.
    Pre-conditions: GET request with 'pk' (book ID) in the URL.
    Post-conditions: Returns HTTP Response (200 OK) with book details, or 404 Not Found.
    '''
    def get(self, request: Request, pk: int, *args, **kwargs) -> Response:
        return Response({"message": "to implement"})

class UserLibraryPreferencesAPIView(APIView):
    """
    Prototype: Handles the request to display the preferences of a specific user regarding the library.
    Pre-conditions: GET request with 'pk' (user ID) in the URL.
    Post-conditions: Returns HTTP Response (200 OK) with user library preferences, or 404 Not Found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        user_preferences_service = UserProfileService()
        preferences = user_preferences_service.get_user_preferences(request.user.id)
        return JsonResponse({"preferences": preferences})

    def put(self, request: Request, *args, **kwargs) -> JsonResponse:
        user_preferences_service = UserProfileService()
        Dict = dict
        user_preferences = Dict(json.loads(request.body))

        # Find a better way to ensure the user preferences have been updated successfully
        isUpdated = user_preferences_service.update_user_preferences(request.user.id, user_preferences.get('preferences', {}))
        return JsonResponse({"is_updated": isUpdated})

class TitleUpscaleRequestAPIView(APIView):
    '''
    Prototype: Handles the request to launch an upscaling job for a given book.
    Pre-conditions: POST request. Body contains 'book_id' and 'preset_name'. User is authenticated.
    Post-conditions: Returns HTTP Response (202 Accepted) if job is initiated.
      400 Bad Request if invalid parameters or service business error. 404 Not Found if book not found.
    '''
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, title_id: int, *args, **kwargs) -> None:
        booksCatalogService = BooksCatalogService()
        print(request.data)
        booksCatalogService.request_title_upscale(title_id, None, None)
