# user_context_processor
def user_info(request):
    context = {}
    if hasattr(request, 'user_name'):
        context['user_name'] = request.user_name
        context['user_logged_in'] = True

    if hasattr(request, 'user_id'):
        context['user_id'] = request.user_id

    if hasattr(request, 'super_user'):
        context['super_user'] = request.super_user

    return context
