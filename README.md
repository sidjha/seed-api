# seed-api
## API Endpoints

### Collection endpoints

* GET /seeds?lat=xx.xx,lng=yy.yy

> Returns a list of seeds near the current lat and long coordinates.

### Seed endpoints

* GET /seed?seed_id=xxxxxxx    

> Returns a Seed with the specified seed_id.

* POST /seed/create?title=XXXX&link=YYYY&circle=ZZZZ&username=ABC123&lat=xx.xx&lng=xx.xx

> Create a new seed with the specified title and link at the specified coordinates.

* POST /seed/delete?seed_id=XXX

> Delete the specified seed.

* POST /reseed?seed_id=xxxx&username=ABC123&circle_id=yyyy

> Reseed an existing seed in a new specified circle from the specified user’s seedbag. Return error if the circle_id is the same as the seed’s original circle.

### User endpoints

* POST /user/create?first_name=XXXX&last_initial=YYYY&username=xxxx

> Create a new user with the specified first name, last initial and username. All three fields are required.

* GET /user?username=XXXX&user_id=YYYY

> Return the user with the specified username or user_id.

* POST /user/update?username=ABC123&notifications=XX

> Update user with new settings.

* POST /user/delete?username=ABC123

> Delete the specified user.

### Seedbag endpoints

* GET /seedbag?username=XXXX

> Return the seedbag for the specified user.

* POST /seedbag/add?seed_id=XXXX&seedbag_id=YYYY

> Add the specified seed in the specified seedbag.

* POST /seedbag/delete?seed_id=XXXX&seedbag_id=YYYY

> Delete the specified seed from the specified seedbag.

