def cart_count(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values()) if cart else 0}
