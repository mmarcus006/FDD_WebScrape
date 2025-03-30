#Web Scraping Project

#Overview
- the goal of this project is to scrape the website https://apps.dfi.wi.gov/apps/FranchiseEFiling/activeFilings.aspx and extract all franchise disclosure documents from the website as well as metadata regarding the franchises and the companies that own them.

#Steps to Complete Project
1. Create a sqlite database to store the data and create a schema for the data.
    - Table 1: Active Filings
        - Column 1: PrimaryID
        - Column 2: Franchise Name
        - Column 3: Expiration Date
        - Column 4: Active State
        *Note* - Active state will be wisconsin for all entries for now, include ability to add other states later.

    - Table 2: Franchise Metadata
        - Column 1: PrimaryID
        - Column 2: Foriegn ID (from activeFilings table)
        - Column 3: File Number
        - Column 4: Legal Name
        - Column 5: Effective Date
        - Column 6: Expiration Date
        - Column 7: Status
        - Column 8: Address Line 1
        - Column 9: Address Line 2
        - Column 10: City
        - Column 11: State
        - Column 12: Zip
        - Column 13: WI Webpage URL

    - Table 3: FDD Metadata
        - Column 1: PrimaryID
        - Column 2: Foriegn ID (from the Franchise Metadata table)
        - Column 3: FDD URL
        - Column 4: FDD File Name
        - Column 5: FDD File Path
        - Column 6: FDD File Size
        - Column 7: FDD File Download Date
        - Column 8: Number of Pages
        
2. Use puppeteer to navigate to the website (https://apps.dfi.wi.gov/apps/FranchiseEFiling/activeFilings.aspx)
and extract the table of active franchise names and expiration dates. and save the data to the database. Also save the html of the page to a file.

3. use puppeteer to navigate to this website: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx

4. Use the list of franchise names from the database to type each one induvidually on the webpage with puppeteer on the following element: 'input#txtName'

5. After typing the franchise name, wait 1 second then click the same element with puppeteer and then send keys 'tab' then 'enter'

6. Wait for new page to load.

7. Retrieve the table from the table and read into a pandas dataframe. below is a snippet of the html for the table:
<table class="SearchResultsControl" cellspacing="0" rules="all" border="1" id="grdSearchResults" style="border-collapse:collapse;">
		<tbody><tr class="SearchResultsHeader" style="white-space:nowrap;">
			<th scope="col"><a href="javascript:__doPostBack('grdSearchResults','Sort$franchiseFilingID')">File Number</a></th><th scope="col"><a href="javascript:__doPostBack('grdSearchResults','Sort$legalName')">Legal Name</a></th><th scope="col"><a href="javascript:__doPostBack('grdSearchResults','Sort$tradeName')">Trade Name</a></th><th scope="col"><a href="javascript:__doPostBack('grdSearchResults','Sort$effectiveDate')">Effective Date</a><img src="images/arrow_down.png"></th><th scope="col"><a href="javascript:__doPostBack('grdSearchResults','Sort$expirationDate')">Expiration Date</a></th><th scope="col"><a href="javascript:__doPostBack('grdSearchResults','Sort$description')">Status</a></th><th scope="col">&nbsp;</th>
		</tr><tr class="SearchResultsOddRow">
			<td>637375</td><td>1 800 FLOWERS.COM FRANCHISE CO INC</td><td>1-800-FLOWERS; 1-800-FLOWERS.COM</td><td>10/18/2024</td><td>10/18/2025</td><td>Registered</td><td><a href="details.aspx?id=637375&amp;hash=1758030309&amp;search=external&amp;type=GENERAL">Details</a></td>
		</tr><tr class="SearchResultsEvenRow">
			<td>637007</td><td>1-800-Textiles Franchises, LLC</td><td>1-800-Textiles</td><td>7/9/2024</td><td>7/9/2025</td><td>Registered</td><td><a href="details.aspx?id=637007&amp;hash=1190521760&amp;search=external&amp;type=GENERAL">Details</a></td>
		</tr><tr class="SearchResultsOddRow">
			<td>636911</td><td>1-800-RADIATOR FRANCHISOR SPV LLC</td><td>1-800-RADIATOR &amp; A/C®</td><td>6/23/2024</td><td>6/23/2025</td><td>Registered</td><td><a href="details.aspx?id=636911&amp;hash=2020110519&amp;search=external&amp;type=GENERAL">Details</a></td>
		</tr><tr class="SearchResultsEvenRow">
			<td>636836</td><td>1-800-GOT-JUNK? LLC</td><td>1-800-GOT-JUNK?</td><td>6/7/2024</td><td>6/7/2025</td><td>Registered</td><td><a href="details.aspx?id=636836&amp;hash=636647066&amp;search=external&amp;type=GENERAL">Details</a></td>
		</tr><tr class="SearchResultsOddRow">
			<td>636683</td><td>1-800-Services, LLC</td><td>1-800-Plumber</td><td>5/15/2024</td><td>5/15/2025</td><td>Registered</td><td><a href="details.aspx?id=636683&amp;hash=1720839305&amp;search=external&amp;type=GENERAL">Details</a></td>
		</tr><tr class="SearchResultsEvenRow">
			<td>635990</td><td>1800Packouts Franchise, LLC</td><td>1-800-Packouts</td><td>4/12/2024</td><td>4/12/2025</td><td>Registered</td><td><a href="details.aspx?id=635990&amp;hash=969422224&amp;search=external&amp;type=GENERAL">Details</a></td>
		</tr><tr class="SearchResultsOddRow">
			<td>635001</td><td>1 800 FLOWERS.COM FRANCHISE CO INC</td><td>1-800-FLOWERS; 1-800-FLOWERS.COM</td><td>10/20/2023</td><td>10/20/2024</td><td>Expired</td><td>&nbsp;</td>
		</tr><tr class="SearchResultsEvenRow">
			<td>634569</td><td>1-800-RADIATOR FRANCHISOR SPV LLC</td><td>1-800-RADIATOR &amp; A/C®</td><td>6/28/2023</td><td>6/28/2024</td><td>Expired</td><td>&nbsp;</td>
		</tr><tr class="SearchResultsOddRow">
			<td>634541</td><td>1-800-Services, LLC</td><td>1-800-Plumber</td><td>6/21/2023</td><td>6/21/2024</td><td>Expired</td><td>&nbsp;</td>
		</tr><tr class="SearchResultsEvenRow">
			<td>634398</td><td>1-800-Textiles Franchises, LLC</td><td>1-800-Textiles</td><td>5/23/2023</td><td>5/23/2024</td><td>Expired</td><td>&nbsp;</td>
		</tr><tr class="SearchResultsOddRow">
			<td>634366</td><td>1-800-GOT-JUNK? LLC</td><td>1-800-GOT-JUNK?</td><td>5/19/2023</td><td>5/19/2024</td><td>Expired</td><td>&nbsp;</td>
		</tr><tr class="SearchResultsEvenRow">
			<td>634178</td><td>1800Packouts Franchise, LLC</td><td>1-800-Packouts</td><td>4/30/2023</td><td>4/30/202

8. Filter out all franchises that do not have a registered value in the status column.

9. For each franchise that is registered, extract the metadata from headers of the table and map it to the metadata schema in Table 2 described above. The HREF within the 'Details' value of the column with no header is the link to the franchise details page.

10. Go to the franchise details page and extract the metadata for the business email address which can be found using the following ID as selectors:
Address Line 1: lblFranchiseAddressLine1
Address Line 2: lblFranchiseAddressLine2
City: lblFranchiseCity
State: lblFranchiseState
Zip: lblFranchiseZip

11. Save the extracted metadata to table 2 of the database.

12. use the following URL of the cURL request below as the fdd url value in table 2 of the database.

13. Mimic the cURL request below to download the FDD URL for the franchise, scrape all the dynamic headers from the wisconsin franchise page.

CURL Request:
curl 'https://apps.dfi.wi.gov/apps/FranchiseSearch/details.aspx?id=637375&hash=1758030309&search=external&type=GENERAL' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'cache-control: max-age=0' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -b 'ASPSESSIONIDCUTTCACB=ALEFEPEANDLCPCONHNGPONHB' \
  -H 'dnt: 1' \
  -H 'origin: https://apps.dfi.wi.gov' \
  -H 'priority: u=0, i' \
  -H 'referer: https://apps.dfi.wi.gov/apps/FranchiseSearch/details.aspx?id=637375&hash=1758030309&search=external&type=GENERAL' \
  -H 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' \
  --data-raw '__VIEWSTATEFIELDCOUNT=6&__VIEWSTATE=b5jMes9R%2F53gH5RXfv%2FcbcvF0eWgKJubqfoJ51RcGYI58JJejDMOJQVIVHZxhlByO92lSrb5HnrkyyH6%2Bu2nhkghasu2%2F3vxuKBaw3jkiCiNncCgIM4ws6LPR7yjo%2BTx%2F7vknyyVvbl6fc8zhBepRQyKTi%2BOjkh7jtnP9g8WiQbbxOmOi7liWlbp5BBJCr3ed5ssh66%2FjzK4AvZ3Xamlj4fVg0x1FdlQU1784%2FvC04czuPvYU4d87KRb%2F943NLAPwJ0ztv%2BfH2uLIyL4aNMYiqdkd2hRWIUQUkdZ%2B88vWTv8rdXDC4N%2FxqXH73Edw5f8H9o54CV9KB4KR4T7DaKBEoskmT5SSJzzvp5Pd5Q367s3ANd90isrc9EhPOiy%2FT%2Bo2TnqCYl3gJ%2BwKx3NcjuVTlYMAWuKW9c6%2BQfRmPYhYL9Vs36dvTOKPZ62JnNDETH6hbIyuhVzfp9TOqq%2FWSqwjHbTebJucq9ll6VwEZJ3ZiBHZPKm1O45YOz%2BoKIM%2BTRk&__VIEWSTATE1=q%2BClGbs2wvVtNTIIFO3LcUxSVdSndQv5jtQb7gIzenyoaTBKigARjt%2BJNlegLFIJPMyA6XDjN%2BLKTWHyRA4shGnAFWj4aRyHtGCXiZoLeup3WWD9ma8qVjD8CZ4vWmLWqQkZQ2E7Z8b6hFauCucpNqKR%2BZAi%2F0lc8r6NW6hdYCe%2F1AKm7C6JMsB0aMOHrC8sirdfkKuYet4BsXrNfX3OhQSvLo0ejesvFw7yALjJtqOZmA43W58vui2e1ur4Mg8CKltmYs6SVUIUNxLS9HY7MvqkOjo9BAXNsh%2BrUQ8WkDyFNIb8LD1TOmbXcm%2FlJ2N4LeGReIW2jNzNcivaio47Q272e%2FJtRBeZtjpIRhmxU3nlUM2dl3DpanzNmlIE23mosrj4ua4zOTV9hdr1%2FoTAldYi5WWDX65JSh%2BHE1LYZB%2FgNF4QDuhd5dSV1NemJyFilkFtxSFt6lgsuIokT8I1DGGYi5Q%2BzWJWXRkjdL7fRMEAW1GKcl8wtHk%2FwYY4DTn3&__VIEWSTATE2=LWDqx%2FlPBTEBPy9vbJt%2BzzF0oc8u8VQeauhLoq6s%2B6YydxCLrbv%2FnQHSfW1j0Q%2Fjh4eL2gtnSYegoD6V70YshW%2BWUy7mF%2BL2guYhBCpGlb1mWube9W5JQSi%2F%2BywM9ncU6xWoWfR6pa1jh%2Bmyy%2FY4PDlp53w%2BDKqBlGxnMFQ3HHyxIVmAqWPqsJ%2BTIidtRlFvC9tSEFT2kFMxjOm%2FL525WvIE8XTbbuDepjOPyTOIcC%2BtiquyNb9fvuRNx4S%2BbUXUhy9cgf%2FyEzF9yHlAJPM4RH78NTugt9SQ7MjMgDxwp1gKDXlAc8f56NuxajWeaXNaLTxm7%2FmYDX5rdwUGGnwqb4qldQBSGicqbQT8BYxlz13l%2BbC19KwJNUpMyWmQAsyy4HHg53N6jsqZxXoPD7XqNl0HpNjw6aQ1olEv%2BLR2hyVYEWwqtUDtLeoalV5L0saXwmJC0oyxZzpsVF75KPky7T5u71MmZYXZ6NNTHhD6wZuXjP9tBXJ7YFyBVyQMu7nH&__VIEWSTATE3=Fj0xzC6QHTw5yeGaKXJN4QB34EG6Kr656GA3d7BKt5DZLIN86IXq1QL%2FEXu5ptakr39P7jtsxRwarUQn5sD3%2FYY4w7z5pRYqzQELpTMsafbErapN79N8n9iNn1mNCgHqoMuLGRy7%2FUJbaPxt%2FwFBtLPBSbiwNYkkKAdR%2BZjd7PwK0eLmxIYldaiSg2kOIOc%2B2%2FTFQeRQJYok2cyteqizz80rMcRkKmFJ%2FDo9rPLkjIOTm21CBLopt9k0mBRO%2FUd092WroycweC5aM7LpES%2BQhX2XwQWM1lwFjwHnslThweEBdh5ZDpwo0vFg%2FnNLe1l8XS0%2BwMv61dhlbi%2BKkG9XE7DAjKSYvp8NCXSmnZk8IL%2FDIuBm8hjXnWGzjltBo%2FJ9weJz4LDaTGNs7zQ67C448rl6AF1xUl%2Ft360%2FH5bj2iC%2F9HwfqXd9mVh91CXiSA3VSqJX4vjIRkq3ACUmAE8pXKyxqk1YWsCGFOPc4CD%2F4DKZ9qnrokhAoL6XMldCHwJy&__VIEWSTATE4=tT2ihRX1HGGMvYMm8YeiyvP7TAJyfJPzdRqo5%2FdbHU65rP3otaP9Da0FPCWnBH6evH4%2B1g7kxaZonK7ey9ypIqX9Vgvg17RDGIfdpO44RHvOGXdMBKsvtamcw9NOO0V7fTqgwShlvZk5hzFyFgHCqqbmlaMaodL8rlH%2Fu4w%2F6OHkbs5kyYVgRBoTuiSoHnTTDNRBerDaLq7GhIEV6CNisSydeA61vm%2BcMuQLZU2e2Y5w6rcVzd2f8ruZ4O5iZDXfyFYtQsHcIKYDsH7ITmXdCaD1IxUM6zUVge3%2F2Wxw8uI8bDSZQbcPG322657BOX5oCMswbOegXhSmpjDizSFnLiiTU3%2FdokKO%2BR5r9XMUbG2zFWSt7q2vw2Zn%2FBhUZN%2BcU7rfgCV9r5veMIhrHO%2FMVtRLN%2Fy7T%2BXKEBbmJVn1WeF5XVgMz5XoJyAzhVxsLcUKzr%2BmrzYxtPSPOG0%2BuX5du%2B%2FyemrkNOj6dLEtZAMMLAQ28MV2GAcoKYfko0mVwIQg&__VIEWSTATE5=gtcDWSfZGLrhAhkkgyd8krCdEHmfKM1JPmZs8ePlLBvAPYmY7y%2Fsw7Q%2FksOyseeF%2FDje1VsjSOEKK4ClgI2k7fwV8rwVfM%2FVtNUjf78TFooN2FyNtse4wXDIH6AdNei3ZSBB%2BYb9eRrhzbS9VQIeybUqrUexmaJ1TO%2F8JXLFRIkLKaIpY%2BKUjO2eOjWC%2FDxG2CWVNsLdSBfCToY60a71shj629Hp1vlr2lSWVmWjbjNevMVTp1dxfaNwkVq%2BHfo9kz8cE8Vf72P%2BRifUpp3EsLdFKfw18RQCre0m8seNvjeEov%2F%2FMijqJXARm2qMld%2FzHj82JKB7keCbHKt5pnWZVm1AKtv8xe24PTuhsn20OO0UrhR4QEV0BBuaOhJp2%2B5ZsBUJGCMi4%2FvJBFJPmACrO6NfeANQ1kI7KX3GUi%2FVIz6fgcW8SrZpd60TrhPUnLIuyiytic7NSfq9d%2FCI9vemIl7rnHMqFTfScNzT1AdXuzw%3D&__VIEWSTATEGENERATOR=D6E137EF&__VIEWSTATEENCRYPTED=&upload_downloadFile=Download'

14. Move the downloaded FDD file to the data/fdds folder, and change the name to the file id number extracted earlier + _ + Franchise Name + Year of Effective Date + .pdf

15. Extract data described in Table 3 from the FDD and upload to sqlite database.

16. Repeat steps 3-15 for each franchise in the database.
