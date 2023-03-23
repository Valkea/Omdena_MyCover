# Deploying an AWS RDS PostgreSQL instance

## 1. Create a RDS (Relational Database Service) instance of Postgres
> 1. Search *RDS* in the search box in the top (or *Database* in the list of services)
> 2. Click the `Create database` button
> 3. From the list of available options, select: Standard / Postgres / (Free Tier | Production)
> 4. Choose a `master username` (i.e. postgres)
> 5. Choose a `password` (i.e. postgres) and confirm
> 6. In *Connectivity* set `Public access` to `Yes` (if you want to access it from outside the VPC group - EC2 not in group / remote access / ...) otherwise set `No`
> 6. In *Connectivity* set `Existing VPC security groups` to the very same group as the EC2 instance (use same zone) or create a new 
> 7. Click `Create database`


## 2. Accessing RDS from EC2

The RDS instance should be reachable from the EC2 instance if theyr are both in the same security group.
However if this is not the case the following procedure might help setting up the security groups correctly.

### Checking the access from EC2
> 1. Login using your ssh command
>	- `ssh -i my_key_pair.pem ubuntu@[EC2 Public IPv4 DNS]`
> 2. `telnet [RDS Endpoint] 5432`
>	- if it timout or return and error, the access is not correctly configured
> 	- if it grant access then you should be able to access it using your app.
> 3. if psql is installed on your EC2 you can try to connect with it:
>	- `psql --host=[RDS Endpoint] --port=5432 --username=postgres --password --dbname=postgres`

### Setup EC2 / RDS connection
> 1. Select your database in the database list
> 2. Use *Action* / `Setup EC2 connection`
> 3. Choose your EC2 instance
> 4. Review and confirm
> 5. Check access again


## 3. Accessing RDS from outside AWS

### Checking the access from EC2
> 1. `telnet [RDS Endpoint] 5432`
>	- if it timout or return and error, the access is not correctly configured
> 	- if it grant access then you should be able to access it using your app.
> 2. if psql is installed on your computer you can try to connect with it:
>	- `psql --host=[RDS Endpoint] --port=5432 --username=postgres --password --dbname=postgres`

### Setup your public RDS access
> 1. Click your database in the database list
> 2. Go to *Connectivity & security* Check that your database has `publicly accessible` set to *Yes*
> 2. Go to *Connectivity & security* and click on the associated security group
> 3. Go to *Inbound rules* and click `Edit inbound rules`
> 4. Add rule with :
> 	- type: PostgreSQL
> 	- source: 0.0.0.0/0 (or only your IP...)
> 5. Click `Save rules`

At this point the RDS instance might be reachable from the outiside. But if it's not you will need some extra modifications.

### Setup gateway to access Internet from the AWS instances
> 1. Search *VPC* in the search box in the top (or *Network & content delivery* in the list of services)
> 2. Go to *Route Tables*
> 3. Click `Create Route Table` if you haven't one
> 4. (Optional) If you haven't one (or want a special one), click *Create Route Table*, then select your VPC, and then choose Yes, Create.
> 5. Click on the created route table (or on the 'main' route table if you have one)
> 6. Go to *Routes*, click `Edit`
> 7. Add another route, and add the following routes as necessary.
> 	- For IPv4 traffic, specify 0.0.0.0/0 in the Destination box, and select the internet gateway ID in the Target list.
> 	- For IPv6 traffic, specify ::/0 in the Destination box, and select the internet gateway ID in the Target list.
> 8. Click `Save`
>
> source: https://bobcares.com/blog/cant-connect-to-aws-rds-instance/
