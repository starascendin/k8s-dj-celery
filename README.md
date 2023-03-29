# AI ninjas

## Local dev setup

using supabase cuz it takes care of a lot of the plumbing that i don't have to manually do.
I'm mainly using supabase for:
- graphql -- it autogen things based on the table relationships. Use supabase for all graphql things "Query, mutation, subscriptions" etc
- user auth -- i'm gonna use supabase's auth for frontend. (DJ's just leave it there)

For django, the things i am using it for are:
1. django model orm. Define models in django, then run "makemigrations" and migrate against supabase PG.
2. API layer. Use django for 1off apis
3. command line + script executions. 

Basically, use supabase as the main PG + graphql + api layer. Then DJ as the ORM, script exec.


### Run supabase
install supabase cli

then

`supabase start`
`supabase stop --backup` this creates a dump of your local pg. Next time when you run start, pg will be restored

### Run docker
Run docker-compose
`docker-compose up -d --build`



## Run locally

Turn on poetry shell and set env variable

```
poetry shell

export DJANGO_READ_DOT_ENV_FILE=True

```

### Run scripts locally
Put scripts in `./scripts` folder


# Branching

* `dev` -- this is the dev branch.
* `main` -- production branch. Should be stable.
* `do` -- this is the production branch that runs on DO. Cuts from main branch


# OpenAPI gen doc
9131  npx @openapitools/openapi-generator-cli generate \\n  -i api-spec.json \\n  -g typescript-fetch \\n  -o generated-client \\n  --additional-properties=supportsES6=true
 9132  npx @openapitools/openapi-generator-cli generate \\n  -i http://localhost:8012/api/openapi.json \\n  -g typescript-fetch \\n  -o generated-client \\n  --additional-properties=supportsES6=true
 9133  which openapi
 9134  mv ~/Downloads/openapi.json .
 9135  npx @openapitools/openapi-generator-cli generate \\n  -i openapi.json \\n  -g typescript-fetch \\n  -o generated-client \\n  --additional-properties=supportsES6=true