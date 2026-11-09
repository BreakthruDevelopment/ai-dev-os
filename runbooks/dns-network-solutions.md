# DNS records at Network Solutions (superseded)

> **Superseded.** DNS for `breakthruventures.ai` is now hosted at **Cloudflare**, and each app's records are created
> automatically by Terraform when it's deployed with a `domain` in `apps.yaml`. Nobody adds records by hand. See the
> [`30-apps-infra` README, "Custom domains and DNS (Cloudflare)"](https://github.com/BreakthruDevelopment/30-apps-infra#custom-domains-and-dns-cloudflare).
> This page is kept for history only; don't follow it.

DNS for `breakthruventures.ai` stays at Network Solutions, and records are added by hand: one per app, about 30
over the month. Existing records for the website and email are never edited.

## Adding an app's record

1. Sign in at networksolutions.com → **My Domains** → `breakthruventures.ai` → **Manage DNS** (Advanced DNS).
2. Add the record the deploy step printed. It's almost always:

   | Type | Host | Points to | TTL |
   | --- | --- | --- | --- |
   | CNAME | `app7` | the cloud's endpoint, e.g. `xyz.azurecontainerapps.io` | 1 hour |

   What it points to depends on the cloud:

   | Cloud | Record | Value |
   | --- | --- | --- |
   | Azure | CNAME | the app's `*.azurecontainerapps.io` address |
   | Google Cloud | CNAME | `ghs.googlehosted.com` |
   | AWS | CNAME | the API Gateway custom domain's target (`d-….execute-api.us-east-2.amazonaws.com`) |
   | Oracle | A | the VM's public IP, `141.148.159.122` |
3. Some clouds also need a **TXT** record to prove domain ownership before issuing a certificate (Azure
   Container Apps, Google Cloud Run, and AWS's certificate check). Add it exactly as printed; it can be removed after
   the certificate is issued.

   Custom domains are new on Day 1: `apps.yaml` already sets each app's `APP_URL` from its `domain`, but the
   per-cloud domain binding (and printing these records) is added to `30-apps-infra` with app 1.
4. Save, then check: `dig +short app7.breakthruventures.ai` (or an online DNS checker). Changes usually show
   within minutes but can take up to an hour.

## Moving an app to the permanent Oracle host later

Add `oci` to the app's `clouds` in `apps.yaml`, wait for it to come up, then edit that app's record only: change
the CNAME to an A record with the Oracle VM's IP. Nothing in the app changes, because its URL comes from `APP_URL`.

## Never

- Don't edit or delete the root (`@`), `www`, `MX`, SPF/DKIM `TXT` or other records that serve the website and email.
- Don't change the domain's nameservers.
