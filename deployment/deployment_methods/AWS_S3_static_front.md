# Deploying a static page (our simple front-end) on AWS

Sources:
- https://aws.amazon.com/getting-started/hands-on/host-static-website/
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html


## 1. Using AWS S3

### Create S3 bucket
> 1. Search *S3* in the search box in the top (or *Storage* in the list of services)
> 2. Click the `Create bucket` button
> 3. Enter bucker name (i.e. omdenamycover)
> 4. Click `Create` 
> 5. On the S3 ressource / *Object* click `Upload` and send your files


### Configure Static Website
> 1. On the S3 ressource / *Properties* / *Static web hosting* click `Edit`
> 2. Under *Static website hosting* choose `Enable`
> 3. In Index document, enter the file name of the index document, typically index.html
> 4. Click `Save changes`
> 5. The URL is available in S3 ressource / *Properties* / *Static web hosting*
> 6. Don't forget to add the folder path to the url (i.e. http://omdenamycover2.s3-website-eu-west-1.amazonaws.com/v04 )

### Configure public access
> 1. Go on the S3 ressource / *Permissions* 
> 2. Click `Edit` on *Block public access* and uncheck `Block all public access`
> 3. Click `Edit` on *Bucket Policy* and add the following policy (with right bucket name)
> ```
> {
>     "Version": "2012-10-17",
>     "Statement": [
>         {
>             "Sid": "PublicReadGetObject",
>             "Effect": "Allow",
>             "Principal": "*",
>             "Action": [
>                 "s3:GetObject"
>             ],
>             "Resource": [
>                 "arn:aws:s3:::omdenamycover/*"
>             ]
>         }
>     ]
> }
> ``` 
> 4. Click `Save change`


## 2. Using AWS Amplify
Another approach is to use AWS Amplify

### Create an Amplify instance
> 1. Search *Amplify* in the search box in the top (or *Front-end Web & Mobile* in the list of services)
> 2. Click the `Get started` button at the top
> 3. Click the `Get started` button bellow the *Amplify Hosting*
> 4. Connect your GitHub, Bitbucket, GitLab, or AWS CodeCommit repositories. 
> 5. Keep the default settings
> 6. Review and `Create`

### Configure to point on the right directory
> 1. Go to "App settings" / `Rewrite and redirects`
> 2. Click `Edit`
> 3. Change target address for base path to expected entrypoint (i.e. deployment/client_html_js/v04/index.html)

### Solve *mixed active content* problem with AWS CloudFront

Where deploying on AWS Amplify we are given a https address, but our EC2 instance has a http address, so we will have *mixed active content* problems. To solve this, we need to configure our app with https (which isn't the case), use a CloudFront instance to map https to http or simply deploy on static S3 (which has http by default)

So the easiest way to deploy a static content able to connect the current API endpoint is AWS with S3.
