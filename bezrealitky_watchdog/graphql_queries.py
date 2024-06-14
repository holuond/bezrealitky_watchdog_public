import requests

BEZREALITKY_GRAPHQL_ENDPOINT = 'https://api.bezrealitky.cz/graphql/'


def fetch_advert_markers():
    query = """
        query MarkerList(
          $estateType: [EstateType],
          $offerType: [OfferType],
          $priceTo: Int,
          $regionOsmIds: [ID],
          $currency: Currency,
          $disposition: [Disposition],
          $equipped: [Equipped],
          $surfaceTo: Int,
          $roommate: Boolean,
          $availableFrom: DateTime
        ) {
          markers: advertMarkers(
            offerType: $offerType,
            estateType: $estateType,
            priceTo: $priceTo,
            regionOsmIds: $regionOsmIds,
            currency: $currency,
            disposition: $disposition,
            equipped: $equipped,
            surfaceTo: $surfaceTo,
            roommate: $roommate,
            availableFrom: $availableFrom
          ) {
            id
            uri
            gps {
                lat
                lng
            }
          }
        }
        """

    # TODO configure this according to your needs
    variables = {
        "offerType": ["PRONAJEM"],
        "estateType": ["BYT"],
        "priceTo": 20000,
        "regionOsmIds": ["R435541"],
        "currency": "CZK",
        "disposition": ["DISP_1_KK", "DISP_1_1", "GARSONIERA"],
        "equipped": ["CASTECNE", "VYBAVENY"],
        "surfaceTo": 70,
        "roommate": False,
        "availableFrom": 1719784800
    }
    response = requests.post(BEZREALITKY_GRAPHQL_ENDPOINT, json={'query': query, 'variables': variables}, headers={'Content-Type': 'application/json'})
    return response.json()['data']['markers']


def fetch_advert(advert_id):
    query = """
    query GetAdvert($id: ID!) {
        advert(id: $id) {
            id
            uri
            reserved
            availableFrom
            visitCount
            conversationCount
            gps {
                lat
                lng
            }
            address(locale: CS)
            price
            charges
            serviceCharges
            utilityCharges
            fee
            surface
            surfaceLand
            disposition
            ownership
            roommate
            parking
            garage
            heating
            floor
            reconstruction
            water
            sewage
        }
    }
    """
    variables = {"id": advert_id}
    response = requests.post(BEZREALITKY_GRAPHQL_ENDPOINT, json={'query': query, 'variables': variables}, headers={'Content-Type': 'application/json'})
    return response.json()['data']['advert']
