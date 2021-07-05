from rest_framework.views import exception_handler

def custom_exception_handler(exc,context):

    handlers={
        'ValidationError': _handle_generics_errror,
        'NotFound': _handle_notfound_errror,
        'NotAuthenticated': _handle_authentication_errror,
        'Forbiden' : _handle_forbiden_errror
    }

    response=exception_handler(exc,context)

    # if response is not None:
    #     response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc,context,response)
    return response


def _handle_authentication_errror(exc,context,response):

    response.data = {
        "code" : "HTTP_401_UNAUTHORIZED",
        "msg" : "Authenticate credentials were not provide",
        "status" : "401"
    }    

    return response

def _handle_generics_errror(exc,context,response):

    response.data = {
        'error' : 'ข้อมูลไม่ถูกต้อง',
        'code' : 'VALIDATION_ERROR',
    } 

    return response

def _handle_notfound_errror(exc,context,response):

    response.data = {
        'code' : 'HTTP_404_NOT_FOUND',
        'msg'  : 'ไม่พบข้อมูล'
    } 

    return response

def _handle_forbiden_errror(exc,context,response):

    response.data = {
        'code' : 'HTTP_403_FORBIDDEN',
        'msg'  : 'ไม่มีสิทธิ์เข้าใช้งาน'
    } 

    return response