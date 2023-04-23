from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Listings, Location, Reviews, Property_Details, Amenities
from rest_framework.decorators import api_view
import json 

def Merge(dict1, dict2):
	res = dict1 | dict2
	return res

# Create your views here.

@api_view(['GET'])
def getListings(request):
    listings = list(Listings.objects.all().values())
    location = list(Location.objects.all().values())
    json_data = []
    for i in listings:
        for j in location:
            if i['id'] == j['listing_id_id']:
                print(i, " mapping with ",j)
                data = {
                    "id": i['id'],
                    "name": i["name"],
                    "city": j["city"],
                    'neighbourhood': j["neighbourhood"],
                    'listing_id_id': j["listing_id_id"]}
                json_data.append(data)
                break
                
    return JsonResponse(json_data, safe=False)

# @api_view(['GET'])
# def getCities(request):
#     cities = list(Location.objects.order_by().values('city').distinct())
#     return JsonResponse(cities, safe=False)

# Nidhi Galgali
# Get listings of cities.
@api_view(['GET'])
def list_cities(request):
   cities = Location.objects.values_list('city', flat=True).distinct()
   cities = [city for city in cities]
   return JsonResponse({'cities': cities})


# Nidhi Galgali
# Get listings in  a particular cities.
@api_view(['GET'])
def city_listings(request, city):
   listings = Listings.objects.filter(location__city=city)
   data = [{'id': listing.id, 'name': listing.name} for listing in listings]
   return JsonResponse({'listings': data})

# Nidhi Galgali
# Get property details.
@api_view(['GET'])
def listing_details(request, listing_id):
    try:
        property_details = Property_Details.objects.get(listing_id=listing_id)
        amenities = Amenities.objects.filter(listing_id=listing_id).first()
        ratings = Reviews.objects.filter(listing_id=listing_id).first()
        locations = Location.objects.filter(listing_id=listing_id).first()
    except Property_Details.DoesNotExist:
        return JsonResponse({'error': 'listing ID does not exist'}, status=404)

    data = {
        'neighbourhood': locations.neighbourhood.strip("'"),
        'price': property_details.price,
        'bedrooms': property_details.bedrooms,
        'accomodate_count': property_details.accomodate_count,
        'amenities': amenities.amenities.strip("'") if amenities else None,
        'rating': ratings.score_value
    }

    return JsonResponse(data, status=200)


@api_view(['POST'])
def addListings(request):
    json_data = json.loads(request.body.decode('utf-8'))
    id = json_data['listingId']
 
    listings = Listings.objects.get(id=id)
    if 'Listingname' in json_data.keys():
        listings.name = json_data['Listingname']

    location = Location.objects.get(listing_id=id)
    if 'longitude' in json_data.keys():
        location.longitude = json_data['longitude']
    if 'latitude' in json_data.keys():
        location.latitude = json_data['latitude']
    if 'city' in json_data.keys():
        location.city = json_data['city']
    if 'neighbourhood' in json_data.keys():
        location.neighbourhood = json_data['neighbourhood']

    review = Reviews.objects.get(listing_id = id)
    if 'score_rating' in json_data.keys():
        review.score_rating = json_data['score_rating']
    if 'score_value' in json_data.keys():
        review.score_value = json_data['score_value']

    details = Property_Details.objects.get(listing_id = id)
    if 'propert_type' in json_data.keys():
        details.property_type = json_data['propert_type']
    if 'room_type' in json_data.keys():
        details.room_type = json_data['room_type']
    if 'accomodate_count' in json_data.keys():
        details.accomodate_count = json_data['accomodate_count']
    if 'bedrooms' in json_data.keys():
        details.bedrooms = json_data['bedrooms']
    if 'price' in json_data.keys():
        details.price = json_data['price']
    if 'instant_bookable' in json_data.keys():
        details.instant_bookable = json_data['instant_bookable']

    amenities = Amenities.objects.get(listing_id = id)
    if 'amenities' in json_data.keys():
        amenities.amenities = json_data['amenities']

    print(listings)
    listings.save()
    location.save()
    review.save()
    details.save()
    amenities.save()

    return JsonResponse({"meassage": "OK"})

#@csrf_exempt
@api_view(['DELETE'])
def delete_property(request, listing_id):
    try:
        property_details = Property_Details.objects.get(listing_id=listing_id)
        reviews=Reviews.objects.get(listing_id=listing_id)
        location=Location.objects.get(listing_id=listing_id)
        amenities=Amenities.objects.get(listing_id=listing_id)
        
    except Property_Details.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)
    
    property_details.delete()
    reviews.delete()
    location.delete()
    amenities.delete()
    return JsonResponse({'message': 'Property deleted successfully'}, status=204)



@api_view(['PUT'])
@csrf_exempt
def update_listing(request, listing_id):
    try:
        listing = Listings.objects.get(id=listing_id)
    except Listings.DoesNotExist:
        return JsonResponse({'error': 'Listing not found'}, status=404)

    if request.method == 'PUT':
        json_data = request.data

        if 'name' in json_data.keys():
            listing.name = json_data['name']

        try:
            location = Location.objects.get(listing_id=listing_id)
            if 'longitude' in json_data.keys():
                location.longitude = json_data['longitude']
            if 'latitude' in json_data.keys():
                location.latitude = json_data['latitude']
            if 'city' in json_data.keys():
                location.city = json_data['city']
            if 'neighbourhood' in json_data.keys():
                location.neighbourhood = json_data['neighbourhood']
            location.save()
        except Location.DoesNotExist:
            pass

        try:
            review = Reviews.objects.get(listing_id=listing_id)
            if 'score_rating' in json_data.keys():
                review.score_rating = json_data['score_rating']
            if 'score_value' in json_data.keys():
                review.score_value = json_data['score_value']
            review.save()
        except Reviews.DoesNotExist:
            pass

        try:
            details = Property_Details.objects.get(listing_id=listing_id)
            if 'property_type' in json_data.keys():
                details.property_type = json_data['property_type']
            if 'room_type' in json_data.keys():
                details.room_type = json_data['room_type']
            if 'accomodate_count' in json_data.keys():
                details.accomodate_count = json_data['accomodate_count']
            if 'bedrooms' in json_data.keys():
                details.bedrooms = json_data['bedrooms']
            if 'price' in json_data.keys():
                details.price = json_data['price']
            if 'instant_bookable' in json_data.keys():
                details.instant_bookable = json_data['instant_bookable']
            details.save()
        except Property_Details.DoesNotExist:
            pass

        try:
            amenities = Amenities.objects.get(listing_id=listing_id)
            if 'amenities' in json_data.keys():
                amenities.amenities = json_data['amenities']
            amenities.save()
        except Amenities.DoesNotExist:
            pass

        listing.save()
        return JsonResponse({'message': 'Listing updated successfully'}, status=200)
