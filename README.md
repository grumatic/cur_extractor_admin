(Temporary README- also found in install-dev.md)

## DEVELOPMENT installation:

* Clone the repository

```
git clone git@github.com:grumatic/cur_extractor_admin.git
```

* Go to the cloned repository's directory

* Create your .env file
(use the existing `.env-SAMPLE` file as template)

* Build through docker-compose

```
docker-compose up --build
```


## Using the CUR Extractor


* After it's built, navigate to [http://localhost:8000](http://localhost:8000)

* Login with the admin username and password.

* You must create (in order):

    * Storage Info
        - The Storage Info ARN's role must have read permission of the bucket selected
        - The original CUR reports will be read from here
    * Payer Acccount
        - The Storage Info you select must be the one which has the account's CUR reports
    * Linked Account (optional)
        - Must be linked with one Payer Account.
        - This account can be use to filter the reports in the Report Info
    * Report Info
        - The Report Info ARN's role must have write permission to the bucket entered
        - The report will be generated according to the Payer account selected.
        - The fields which have its cross box selected, will be included in the report.
        if you wish to remove them, you should unselect their respective cross box.
        - The accounts can be selected for more granular filtering. If no account is selected, all accounts included in the payer account's report will included in the report.
