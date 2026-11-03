# DNS records at Network Solutions

DNS for `breakthruventures.ai` stays at Network Solutions, and records are added by hand: one per app, about 30
over the month. Existing records for the website and email are never edited.

## Adding an app's record

1. Sign in at networksolutions.com → **My Domains** → `breakthruventures.ai` → **Manage DNS** (Advanced DNS).
2. Add the record the deploy step printed. It's almost always:

   | Type | Host | Points to | TTL |
   | --- | --- | --- | --- |
   | CNAME | `app7` | the cloud's endpoint, e.g. `xyz.azurecontainerapps.io` | 1 hour |

   For the Oracle VM it's an **A** record pointing at the VM's public IP instead.
3. Some clouds also need a **TXT** record to prove domain ownership before issuing a certificate (Azure
   Container Apps, Google Cloud Run). Add it exactly as printed; it can be removed after the certificate is issued.
4. Save, then check: `dig +short app7.breakthruventures.ai` (or an online DNS checker). Changes usually show
   within minutes but can take up to an hour.

## Moving an app to the permanent Oracle host later

Edit that app's record only: change the CNAME to an A record with the Oracle VM's IP. Nothing in the app changes,
because its URL comes from the `APP_URL` setting.

## Never

- Don't edit or delete the root (`@`), `www`, `MX`, SPF/DKIM `TXT` or other records that serve the website and email.
- Don't change the domain's nameservers.
