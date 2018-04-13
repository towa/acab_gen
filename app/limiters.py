from flask_limiter.util import get_remote_address

def vote_limiter(request):
    content = request.get_json(silent=True)
    if ((u'b' in content) and (u'c' in content)):
        down = False
        if (u'downvote' in content):
            down = content.get('downvote')
        c = content.get('c')
        b = content.get('b')
        return (get_remote_address() + b + c + str(down))
