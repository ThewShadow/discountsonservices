from paypalcheckoutsdk.core import PayPalHttpClient
from paypalcheckoutsdk.core import SandboxEnvironment
from paypalcheckoutsdk.core import LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalhttp import HttpError

import json

# PayPal's client ID and secret
PP_CID = "AQtEer1_nUi9pF61tztIprWrH3XLq8kpmB7qYj2godQX2tciY6x-hFTPHuRKSW0Ap5ozDQERVj-qwqFX"
PP_SEC = "EP94tIaw0ftSIDnbWZI0m3-UDNyRhbYRJ5_Mk5E_vwobu33lzuo4kHzZ6LPSD4oRwJ84l4rTVQaQAUai"

class PayPalOrderStatus():
    created = 'CREATED'
    completed = 'COMPLETED'
    notprocessed = 'UNPROCESSABLE_ENTITY'


class PayPalOrdering():
    """ Creates order for user to pay
    """

    def __init__(self, PP_CID, PP_SEC, debug=False):
    #def __init__(self, PP_CID, PP_SEC, debug=True):
        if debug:
            self.environ = SandboxEnvironment(
                client_id=PP_CID, client_secret=PP_SEC
            )
        else:
            self.environ = LiveEnvironment(
                client_id=PP_CID, client_secret=PP_SEC
            )

        self.client = PayPalHttpClient(self.environ)

    def create_order(self, ammount):
        request = OrdersCreateRequest()

        request.prefer('return=representation')

        request.request_body(
            {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "frequency": "MONTH",
                        "cycles": "12",
                        "amount": {
                            "currency_code": "USD",
                            "value": str(ammount)
                        }
                    }
                ]
            }
        )

        try:
            response = self.client.execute(request)

            if response.status_code == 201:
                is_found = False
                for link in response.result.links:
                    if link.rel == "approve":
                        is_found = True
                        return {
                            'link': link.href,
                            'id': response.result.id
                        }

                if not is_found:
                    return False

        except IOError as ioe:
            print(ioe)
            if isinstance(ioe, HttpError):
                print(ioe.status_code)
                return False

    def check_order(self, order_id: str):
        request = OrdersCaptureRequest(order_id)

        try:
            response = self.client.execute(request)

        except Exception as ex:
            useful_ex = json.loads(ex.message)
            if isinstance(ex, HttpError):
                # import pdb; pdb.set_trace()
                if useful_ex['name'] == PayPalOrderStatus.notprocessed:
                    return False

                print(ex)
                print(ex.status_code)
                return False
            else:
                return False

        return True


# if __name__ == '__main__':
#     pp_payment = PayPalOrdering(PP_CID, PP_SEC)
#     order = pp_payment.create_order(1.00)
#     print(order['link'])
#     pp_payment.check_order(order['id'])
