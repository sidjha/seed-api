# seed-api
## Endpoints

* GET /circles?lat=xx.xx,lng=yy.yy

> Returns a matching circle if the specified latitude and longitude fall within a defined circle. Otherwise, returns a list of nearby circles based on specified latitude and longitude.

* GET /seeds?circle_id=xxxxxxx

> Returns a list of seeds in the circle with specified circle ID.

* GET /seed?seed_id=xxxxxxx    

> Returns a Seed with the specified seed_id.

* POST /seed/create?title=XXXX&link=YYYY&circle=ZZZZ&username=ABC123

> Create a new seed with the specified title and link in the specified circle.

* POST /seed/delete?seed_id=XXX

> Delete the specified seed.

* POST /reseed?seed_id=xxxx&username=ABC123&circle_id=yyyy

> Reseed an existing seed in a new specified circle from the specified user’s seedbag. Return error if the circle_id is the same as the seed’s original circle.

* POST /user/create?first_name=XXXX&last_initial=YYYY&username=xxxx

> Create a new user with the specified first name, last initial and username. All three fields are required.

* GET /user?username=XXXX&user_id=YYYY

> Return the user with the specified username or user_id.

* POST /user/update?username=ABC123&notifications=XX

> Update user with new settings.

* POST /user/delete?username=ABC123

> Delete the specified user.

* GET /seedbags?username=XXXX

> Return the seedbag for the specified user.

* POST /seedbags/add?seed_id=XXXX&seedbag_id=YYYY

> Add the specified seed in the specified seedbag.

* POST /seedbags/delete?seed_id=XXXX&seedbag_id=YYYY

> Delete the specified seed from the specified seedbag.

