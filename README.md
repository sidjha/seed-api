# seed-api
## Endpoints

* GET /circles?lat=xx.xx,lng=yy.yy

> Returns a matching circle if the specified latitude and longitude fall within a defined circle. Otherwise, returns a list of nearby circles based on specified latitude and longitude.

* GET /seeds?circle_id=xxxxxxx

> Returns a list of seeds in the circle with specified circle ID.

* GET /seed?seed_id=xxxxxxx    

> Returns a Seed with the specified seed_id.

* POST /accounts/create?first_name=XXXX&last_initial=YYYY&username=xxxx

> Create a new account with the specified first name, last initial and username. All three fields are required.

* GET /users?username=XXXX&user_id=YYYY

> Return the user with the specified username or user_id.

* GET /seedbags?username=XXXX

> Return the seedbag for the specified user.

* POST /seedbags/add?seed_id=XXXX&seedbag_id=YYYY

> Add the specified seed in the specified seedbag.

* POST /seedbags/delete?seed_id=XXXX&seedbag_id=YYYY

> Delete the specified seed from the specified seedbag.

* POST /seeds/create?title=XXXX&link=YYYY&circle=ZZZZ&username=ABC123

> Create a new seed with the specified title and link in the specified circle.

* POST /reseed?seed_id=xxxx&username=ABC123&circle_id=yyyy

> Reseed an existing seed in a new specified circle from the specified user’s seedbag. Return error if the circle_id is the same as the seed’s original circle.

* POST /users?username=ABC123&notifications=XX

> Toggle notifications off or on for the specified user.

* POST /seeds/delete?seed_id=XXX

Delete the specified seed.

* POST /users/delete?username=ABC123

Delete the specified user.
