How to order AddressBase from Ordnance Survey
=

 1. Go to https://www.ordnancesurvey.co.uk/sso/login.shtml
 2. Log in, and be mindful of the caveats
   a. Your password for this section will *not* work for the 'shop'
   b. If you mistype the password the first time but get it right second time, it will look as if you still can't get in, but you have done already
 3. You should get redirected to https://www.ordnancesurvey.co.uk/psma/index.html
 4. From there, click on ‘Map data’ > ‘Order data’
 5. Click on ‘My Products’ in the top nav bar (or go directly to https://orders.ordnancesurvey.co.uk/orders/contractList.html )
 6. The next step depends on what you want to do:
   a. If you want to simply re-order an existing order with no changes, you can expand the list of products until you find the one you need, and click ‘View area and re-order’
   b. Or, if you want to order anything even slightly different to what you have ordered before (hint: you probably do), you should instead go to the bottom of the list and click ‘Add Another Product’
 7. The order form is confusing and awkward, with lots of interdependent select boxes. The following example illustrates ordering AddressBase for FTP retrieval with updates via changeset
 8. Select the following:
   a. Order type: Public Sector Mapping Agreement
   b. Product type: AddressBase (NOT “AddressBase Great Britain”!)
 9. You must then draw a rectangle on the map that covers the whole of the map
   a. Use the right-most ‘Show all polygons or full map extent’ to zoom the map out as far as it will go
   b. Use the ‘Draw/erase rectangle’ button to select the entire map
 10. Select these options:
   a. Format: CSV
   b. Delivery: FTP
   c. Future Updates: Changed Features (COU)
 11. Enter a number in the ‘Terminals’ box
   a. This number does not really translate well to website use - after calling O.S. support, it’s clear that the number entered here has no effect upon the price, as under the Public Sector Mapping Agreement we get the data for free.  
   b. So, enter any positive integer in this box - support suggested 100 or 1000
 12. Make sure that the price at the bottom is no longer greyed-out, and showing ‘£0.00 non-chargeable’
 13. Click ‘Add to basket’
 14. Click 'Checkout' - you will be prompted to enter your password again.
 15. Click 'Place order'

Sometime later, there should be an email sent to tools@digital.justice.gov.uk containing an order number for this order

The AddressBaseBasicDownloader class in the postcode-info repo is designed to log onto O.S.’s FTP server and change directory to a top-level dir named after the order number

The directory path on the FTP server is controlled by an environment variable OS_FTP_ORDER_DIR - you can set this value as needed
