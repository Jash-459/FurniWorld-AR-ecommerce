import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, Review
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 
from .models import Order,Product,Address,Cart,Wishlist
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render
from decimal import Decimal
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError
from django.core.mail import send_mail,BadHeaderError
from Furniworld.settings import EMAIL_HOST_USER 
from django.conf import settings
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import datetime
from django.contrib.auth import authenticate,login, logout
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
from django import forms





# Create your views here.

from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

  
     
def newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subject = 'Thank you for subscribing to our NewsLetter'
        message = f"Hello {email}, \n\nYou have successfully subscribed to our newsletter."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        
        # Fetch only the categories marked to show on the homepage
        categories = Category.objects.filter(is_featured = True)
        
        # Fetch featured products
        featured_products = Product.objects.filter(is_featured=True)
        
        # Pass categories and featured products to the template
        return render(request, 'store/index.html', {'categories': categories, 'products': featured_products})
    else:
        return render(request, 'store/index.html')

    

def query(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        query_text = request.POST.get('query')
        
        subject = query_text
        message = f'''Dear {name},
Thank you for contacting FurniWorld. This is an automated response to acknowledge that we've received your inquiry regarding {query_text}.

We are currently reviewing your query, and one of our team members will get back to you as soon as possible. 
Please note that our response time may vary depending on the nature of your inquiry, but we strive to address all queries promptly.

If your matter is urgent or you require immediate assistance, please call our customer support team at +91 755-521-9411.

We appreciate your patience and thank you for considering FurniWorld for your needs. We look forward to assisting you.

Best regards,
FurniWorld'''
        from_email = EMAIL_HOST_USER
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, 'Query received successfully!')
        except BadHeaderError:
            messages.error(request, 'Query failed to send. Please try again later.')
            return render(request, 'store/query.html', {'name': name})
        
        return render(request, 'store/query.html', {'name': name})
    else:
        return render(request, 'store/query.html')

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)

@login_required
def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    reviews = Review.objects.filter(product=product)
    context = {
        'product': product,
        'related_products': related_products,
        'review': reviews

    }
    return render(request, 'store/detail.html', context)

def Review_rate(request):
    if request.method == "POST":
        product_id = request.POST.get('prod_id')
        product = get_object_or_404(Product, id=product_id)
        comment = request.POST.get('comment')
        rate = request.POST.get('rate')
        user = request.user
        reviews = Review.objects.create(user=user, product=product, comment=comment, rate=rate)
        reviews.save()
        messages.success(request,'Review Successfully Posted!')
        return redirect('store:product-detail', slug=product.slug)
    else:
        return render('store:home')


@login_required
def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})

@login_required
def category_products(request, slug):
    # Get the category object based on the slug
    category = get_object_or_404(Category, slug=slug)

    # Retrieve all categories
    categories = Category.objects.filter(is_active=True)

    # Retrieve all products related to the category
    products = Product.objects.filter(category=category, is_active=True)

    # Define PriceRangeForm here within the view
    class PriceRangeForm(forms.Form):
        PRICE_CHOICES = [
            ('1000-5000', 'Under ₹5,000'),
            ('5000-10000', '₹5,000-₹10,000'),
            ('10000-15000', '₹10,000-₹15,000'),
            ('15000-20000', '₹15,000-₹20,000'),
            ('20000-30000', '₹20,000-₹30,000'),
            ('30000-above', '₹above ₹30,000'),
        ]
        price_range = forms.ChoiceField(label='Price Range', choices=PRICE_CHOICES, required=False)

    # Initialize an instance of the form with GET data
    form = PriceRangeForm(request.GET)

    # Check if the form is valid
    if form.is_valid():
        # Get the selected price range from the form
        price_range = form.cleaned_data.get('price_range')

        # Filter products based on the selected price range
        if price_range:
            if price_range == '1000-5000':
                products = products.filter(price__range=(1000, 5000))
            elif price_range == '5000-10000':
                products = products.filter(price__range=(5000, 10000))
            elif price_range == '10000-15000':
                products = products.filter(price__range=(10000, 15000))
            elif price_range == '15000-20000':
                products = products.filter(price__range=(15000, 20000))
            elif price_range == '20000-30000':
                products = products.filter(price__range=(20000, 30000))
            elif price_range == '30000-above':
                products = products.filter(price__gte=30000)

    # Prepare context data to pass to the template
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'form': form,
    }

    # Render the template with the context data
    return render(request, 'store/category_products.html', context)

#search
def search(request):
    q = request.GET.get('q')
    products = Product.objects.filter(title__icontains=q)
    categories = Category.objects.filter(is_active=True)
    category = None

    # Determine the current category based on the search results
    if products.exists():
        # Get the category of the first product in the search results
        category = products.first().category

    # Define PriceRangeForm here within the view
    class PriceRangeForm(forms.Form):
        PRICE_CHOICES = [
            ('1000-5000', 'Under ₹5,000'),
            ('5000-10000', '₹5,000-₹10,000'),
            ('10000-15000', '₹10,000-₹15,000'),
            ('15000-20000', '₹15,000-₹20,000'),
            ('20000-30000', '₹20,000-₹30,000'),
            ('30000-above', '₹above ₹30,000'),
        ]
        price_range = forms.ChoiceField(label='Price Range', choices=PRICE_CHOICES, required=False)

    # Initialize an instance of the form with GET data
    form = PriceRangeForm(request.POST)

    # Check if the form is valid
    if form.is_valid():
        # Get the selected price range from the form
        price_range = form.cleaned_data.get('price_range')

        # Filter products based on the selected price range
        if price_range:
            if price_range == '1000-5000':
                products = products.filter(price__range=(1000, 5000))
            elif price_range == '5000-10000':
                products = products.filter(price__range=(5000, 10000))
            elif price_range == '10000-15000':
                products = products.filter(price__range=(10000, 15000))
            elif price_range == '15000-20000':
                products = products.filter(price__range=(15000, 20000))
            elif price_range == '20000-30000':
                products = products.filter(price__range=(20000, 30000))
            elif price_range == '30000-above':
                products = products.filter(price__gte=30000)

    # Prepare context data to pass to the template
    context = {
        'products': products,
        'categories': categories,
        'total_results': products.count(),
        'category': category,
        'form': form,
    }
    return render(request, 'store/search.html', context)


def search(request):
    q = request.GET.get('q')
    products = Product.objects.filter(title__icontains=q)
    categories = Category.objects.filter(is_active=True)
    category = None

    # Determine the current category based on the search results
    if products.exists():
        # Get the category of the first product in the search results
        category = products.first().category

    context = {
        'products': products,
        'categories': categories,
        'total_results': products.count(),
        'category': category,
    }
    return render(request, 'store/search.html', context)



# Authentication Starts Here
class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # Log in the user after successful registration
            user = form.instance
            login(request, user)
            messages.success(request, "Congratulations! Registration Successful! You are now logged in.")
            return redirect('store:home')  
        else:
            return render(request, 'account/register.html', {'form':form})
        
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect('store:home')
   


@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            flat_no = form.cleaned_data['flat_no']
            building_name = form.cleaned_data['building_name']           
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, flat_no=flat_no, building_name=building_name, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    if request.method == 'GET':
        user = request.user
        product_id = request.GET.get('prod_id')
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.GET.get('quantity', 1))

        # Check whether the Product is already in Cart or Not
        item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
        if item_already_in_cart:
            cp = get_object_or_404(Cart, product=product_id, user=user)
            cp.quantity += 1
            cp.save()
        else:
            Cart(user=user, product=product, quantity=quantity).save()
        
        # Remove the product from the wishlist
        Wishlist.objects.filter(product=product_id, user=user).delete()

        return redirect('store:cart')
    else:
        # Handle GET request appropriately
        return redirect('store:home')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    # using list comprehension to calculate total amount based on quantity
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'total_amount': amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    if request.method == 'POST':
        # Process the checkout form submission
        user = request.user
        address_id = request.POST.get('address')
        
        # Ensure the address ID is provided and valid
        if address_id:
            address = get_object_or_404(Address, id=address_id)
            cart = Cart.objects.filter(user=user)
            for c in cart:
                # Save the order for each product in the cart
                Order.objects.create(user=user, address=address, product=c.product, quantity=c.quantity)
                # Delete the product from the cart after processing the order
                c.delete()
            # Redirect to a success page or any other appropriate page
            return render(request, 'store/success.html')
        else:
            # Handle the case where address ID is not provided
            messages.error(request, "Please select a valid address.")
            return redirect('store:cart')  # Redirect to the cart page or any other appropriate page
    else:
        # Handle GET request to display the checkout form
        user = request.user
        cart_products = Cart.objects.filter(user=user)
        addresses = Address.objects.filter(user=user)
        amount = decimal.Decimal(0)
        for cp in cart_products:
            temp_amount = (cp.quantity * cp.product.price)
            amount += temp_amount
        total_amount = amount
        context = {
            'cart_products': cart_products,
            'amount': amount,
            'total_amount': total_amount,
            'addresses': addresses,
        }
        return render(request, 'store/checkout.html', context)
    

@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Retrieve the order ID from the session metadata
        order_id = session.get('order_id')

        if order_id:
            # Update the order status to mark it as paid
            order = Order.objects.get(id=order_id)
            order.payment_status = 'paid'
            order.save()

            # Optionally, update the cart to remove purchased items
            # Remember to adjust this part based on your cart structure
            Cart.objects.filter(user=order.user).delete()

    return HttpResponse(status=200)

 


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        host = request.get_host()

        
        # Retrieve cart items for the current user
        user = request.user
        order_id = self.request.POST.get('order-id')
        cart_items = Cart.objects.filter(user=user)

        address, _ = Address.objects.get_or_create(user=user, defaults={
            'flat_no': 'Your default flat_no',
            'building_name': 'Your default building_name',
            'locality': 'Your default locality',
            'city': 'Your default city',
            'state': 'Your default state',
            })
        
        # Calculate total amount and gather product names
        line_items = []
        total_amount = 0
        for cart_item in cart_items:
            total_amount += cart_item.product.price * cart_item.quantity
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': int(cart_item.product.price * 100),  # Convert to cents
                    'product_data': {
                        'order_id': order_id,
                        'name': cart_item.product.title,
                    }
                },
                'quantity': cart_item.quantity,
            })

         # Create orders for purchased items
        for cart_item in cart_items:
            Order.objects.create(
                user=user,
                address=address,
                product=cart_item.product,
                quantity=cart_item.quantity,
            )
            cart_item.delete()

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://{}{}'.format(host, reverse('store:success')),
            cancel_url='http://{}{}'.format(host, reverse('store:failure')),
        )
        return redirect(checkout_session.url, code=303)
        
def success(request):
    user_cart_items = Cart.objects.filter(user=request.user)
    return render(request,'store/success.html')

def failure(request):
    return render(request,'store/failure.html')
    



@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).select_related('product').order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': orders})

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

def invoice(request,orderID,productID):
    try:
        order = Order.objects.select_related('product', 'user', 'address').get(id=orderID)
        complete_address = f"{order.address.flat_no}, {order.address.building_name}, {order.address.locality}, {order.address.city}, {order.address.state}"
        
        subtotal = order.product.price * order.quantity
        total_amount = subtotal

        mydict = {
            'orderDate': order.ordered_date,
            'customerName': order.user.username,
            'shipmentAddress': complete_address,
            'productImage': order.product.product_image.url,
            'productName': order.product.title,
            'productQuantity': order.quantity,
            'productPrice': order.product.price,
            'subtotal': subtotal,
            'totalAmount': total_amount,
            }

        return render(request, 'store/invoice.html', mydict)

    except Order.DoesNotExist:
        return HttpResponseNotFound("Order not found")
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {str(e)}")
    

@login_required
def add_to_wishlist(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_wishlist = Wishlist.objects.filter(product=product_id, user=user)
    if item_already_in_wishlist:
       messages.success(request, 'Item already in wishlist')
    else:
        Wishlist(user=user, product=product).save()
    
    return redirect('store:wishlist')

@login_required
def remove_wishlist(request, wishlist_id):
    if request.method == 'GET':
        w = get_object_or_404(Wishlist, id=wishlist_id)
        w.delete()
    return redirect('store:wishlist')

def wishlist(request):
    user = request.user
    wishlist_products = Wishlist.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    # using list comprehension to calculate total amount based on quantity
    wp = [p for p in Wishlist.objects.all() if p.user==user]
    if wp:
        for p in wp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    context = {
        'wishlist_products': wishlist_products,
        'amount': amount,
        'total_amount': amount,
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def ar_view(request):
    prod_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=prod_id)
    
    # Check if the product has a 3D model
    if not product.t_model:  # Assuming 't_model' is the field storing the 3D model file
        return render(request, 'store/arnoview.html')
    
    context = {
        'product': product,
    }
    return render(request, 'store/ar.html', context)

def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')


def admin_login_view(request):
    return render(request, 'accounts/login.html')