# GitHub Codespaces ♥️ Jupyter Notebooks

The modern city of Toronto was formed on January 1, 1998 after amalgamating the six constituent municipalities of Metropolitan Toronto into Toronto

### Elections

These are election of city councillors and the mayor. These do not consider byelections

### 2022 Municipal Election
- Election: 2022-10-24
- 


#### 1997 [^1]
- Election: 1997-10-10


[^1] https://en.wikipedia.org/wiki/1997_Toronto_municipal_election


## Data

### contribution-search-results / 2022
- One table with 
- [2022 Municipal Election - Financial Disclosures](http://app.toronto.ca/EFD/jsf/main/main.xhtml?campaign=17)
    1. Click Search Contributions
    2. Click Submit
    3. Click Export
- Excel file is generated using Javascript, not an esay download link

### Elections – Official Results
- From [Open Date:Elections – Official Results](https://open.toronto.ca/dataset/election-results-official/)
- Has election results from 2022, 2018, 2014, 2010, 2006 and 2003 from Mayor, Councillor, Toronto District School Board Trustee, Toronto Separate School Board Trustee, French Language District School Board Trustee and French Language Separate School Board Trustee
- Each year is stored in a zip file called `{year}-results.zip`

#### 2022
- Readme.txt
> Note there are no results for the French language school boards. Candidates were either acclaimed or the election was voided.
- 2022_Toronto_Poll_By_Poll_All_Offices.xlsx


URLS:
- https://studious-waffle-vgr9x7rqjj4hp745-8001.app.github.dev/database?sql=SELECT%0D%0A++Candidate%2C%0D%0A++Ward%2C%0D%0A++%22Vote+Count%22%0D%0AFROM+%28%0D%0A++SELECT%0D%0A++++Candidate%2C%0D%0A++++Ward%2C%0D%0A++++SUM%28%5BVote+Count%5D%29+as+%22Vote+Count%22%2C%0D%0A++++ROW_NUMBER%28%29+OVER%28PARTITION+BY+Ward+ORDER+BY+SUM%28%5BVote+Count%5D%29+DESC%29+as+rn%0D%0A++FROM%0D%0A++++elections_official_results%0D%0A++GROUP+BY%0D%0A++++Candidate%2C%0D%0A++++Ward%0D%0A%29+subquery%0D%0AWHERE+rn+%3D+1%0D%0AORDER+BY%0D%0A++Ward%2C+%22Vote+Count%22+DESC%3B%0D%0A
- https://studious-waffle-vgr9x7rqjj4hp745-8001.app.github.dev/database?sql=SELECT%0D%0A++%22Candidate%2FRegistrant%22+as+Candidate%2C%0D%0A++CAST%28Ward+AS+INTEGER%29+AS+Ward%2C%0D%0A++ROUND%28SUM%28Amount%29%2C+2%29+AS+Amount%0D%0AFROM%0D%0A++%5Bcontribution-search-results%5D%0D%0AWHERE%0D%0A++%22Registered+for%22+%3D+%27Councillor%27%0D%0A++AND+%28%0D%0A++++%22Contributor+Type%22+%3D+%27Candidate%27%0D%0A++++OR+%22Contributor+Type%22+%3D+%22Candidate+Spouse%22%0D%0A++%29%0D%0AGROUP+BY%0D%0A++%22Candidate%2FRegistrant%22%2C%0D%0A++CAST%28Ward+AS+INTEGER%29%0D%0AORDER+BY%0D%0A++CAST%28Ward+AS+INTEGER%29+ASC%2C%0D%0A++ROUND%28SUM%28Amount%29%2C+2%29+DESC%3B
- https://studious-waffle-vgr9x7rqjj4hp745-8001.app.github.dev/database?sql=WITH+winner+AS+%28%0D%0A++SELECT%0D%0A++++REPLACE%28Candidate%2C+%27%2C+%27%2C+%27+%27%29+AS+Candidate%2C%0D%0A++++--+Adjust+based+on+your+DBMS%27s+syntax%0D%0A++++Ward%2C%0D%0A++++%22Vote+Count%22%0D%0A++FROM%0D%0A++++%28%0D%0A++++++SELECT%0D%0A++++++++Candidate%2C%0D%0A++++++++Ward%2C%0D%0A++++++++SUM%28%5BVote+Count%5D%29+AS+%22Vote+Count%22%2C%0D%0A++++++++ROW_NUMBER%28%29+OVER%28%0D%0A++++++++++PARTITION+BY+Ward%0D%0A++++++++++ORDER+BY%0D%0A++++++++++++SUM%28%5BVote+Count%5D%29+DESC%0D%0A++++++++%29+AS+rn%0D%0A++++++FROM%0D%0A++++++++elections_official_results%0D%0A++++++GROUP+BY%0D%0A++++++++Candidate%2C%0D%0A++++++++Ward%0D%0A++++%29+subquery%0D%0A++WHERE%0D%0A++++rn+%3D+1%0D%0A%29%0D%0ASELECT%0D%0A++csr.%22Candidate%2FRegistrant%22+AS+Candidate%2C%0D%0A++CAST%28csr.Ward+AS+INTEGER%29+AS+Ward%2C%0D%0A++ROUND%28SUM%28csr.Amount%29%2C+2%29+AS+Amount%2C%0D%0A++CASE%0D%0A++++WHEN+w.Candidate+IS+NOT+NULL+THEN+%27True%27%0D%0A++++ELSE+%27False%27%0D%0A++END+AS+IsWinner%0D%0AFROM%0D%0A++%5Bcontribution-search-results%5D+csr%0D%0A++LEFT+JOIN+winner+w+ON+csr.Ward+%3D+w.Ward%0D%0A++AND+REPLACE%28csr.%22Candidate%2FRegistrant%22%2C+%27%2C+%27%2C+%27+%27%29+%3D+w.Candidate%0D%0AWHERE%0D%0A++csr.%22Registered+for%22+%3D+%27Councillor%27%0D%0A++AND+%28%0D%0A++++csr.%22Contributor+Type%22+%3D+%27Candidate%27%0D%0A++++OR+csr.%22Contributor+Type%22+%3D+%27Candidate+Spouse%27%0D%0A++%29%0D%0AGROUP+BY%0D%0A++csr.%22Candidate%2FRegistrant%22%2C%0D%0A++CAST%28csr.Ward+AS+INTEGER%29%0D%0AORDER+BY%0D%0A++CAST%28csr.Ward+AS+INTEGER%29+ASC%2C%0D%0A++++IsWinner+DESC%2C%0D%0A++ROUND%28SUM%28csr.Amount%29%2C+2%29+DESC%3B