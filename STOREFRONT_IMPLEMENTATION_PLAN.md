# Tookio Shop storefront implementation plan

Status: implementation-ready architecture plan based on the `tookio-shop.local` database and the installed Tookio Shop/Frappe source as inspected on 2026-08-11.

## 1. Non-negotiable tenancy rule

A Tookio user can own one or many Shops. Every Product, Sale Invoice, Purchase, report row, storefront, and public order must resolve through the exact `shop` Link on that record.

Never infer a Shop from:

- the newest Shop;
- the first Shop returned for a user;
- a session default;
- the system currency;
- a cached “current shop” that is not also supplied and validated as the record's exact Shop.

The explicit Shop selector in the UI is only a filter and creation aid. It is not the authoritative currency source. The saved record's `shop` is authoritative.

For every seller-side write, enforce this invariant on the server:

```text
record.owner == shop.owner == authenticated user
```

System Managers may receive an explicit administrative bypass. Guest storefront requests use a separate, tightly scoped path that resolves a published storefront to one exact Shop.

## 2. Current live-state audit

### 2.1 Installed versions and site

- Frappe `16.30.0`
- ERPNext `16.31.1`
- Tookio Shop branch `develop`, commit `8131cbb`
- One Frappe site and database; Shops are tenant records inside that site.

Do not create one Frappe site per merchant Shop. All storefront subdomains must route to this single Tookio Shop Frappe site.

### 2.2 Current plan records

| Database plan | Price | Shop limit | Product limit | Invoice limit | What `0` currently means |
| --- | ---: | ---: | ---: | ---: | --- |
| Free Plan | KES 0 | 1 | 25 | 100 | N/A |
| Starter Plan | KES 450 | 1 | 100 | 0 | Unlimited invoices |
| Premium Plan | KES 1,160 | 0 | 0 | 0 | Unlimited shops, products, and invoices |

The public pricing/subscription pages do not match these records. They advertise `Free`, `Starter`, and `Pro`, with hard-coded USD prices of `$0`, `$3.50`, and `$9`. There is no `Pro Plan` database record today; the KES 1,160 `Premium Plan` is effectively the advertised Pro tier.

The runtime also disagrees with the plan records:

- Free is hard-coded in several Python paths as 1 Shop, 50 Products, and 200 Sale Invoices.
- An existing Starter subscription has copied limits of 1/150/unlimited, while the current Starter plan says 1/100/unlimited.
- Non-Free enforcement re-reads plan values, while Free enforcement often uses hard-coded values.
- The daily expiry hook calls a no-op function. Expiry is instead handled opportunistically during some API calls and inserts.

These mismatches must be normalized before storefront entitlement checks are trusted.

### 2.3 Current ownership permissions

Shop, Sale Invoice, Tookio Purchase, and Tookio User Subscription give `Tookio Seller` permissions with `if_owner = 1`.

Product has two Tookio Seller permission rows: one owner-only read/write/create row and another unrestricted read/report row. Because permissions are additive, the second row can expose every seller's Products for reads and reports. Remove that unrestricted Product permission.

Creator-only DocType permissions are necessary but not sufficient. Current controllers do not consistently prove that a linked Product belongs to the selected Shop or that the selected Shop belongs to the document owner. Add those relational ownership validations.

### 2.4 Current currency defects

The global default currency is KES. That may remain the platform's fallback and subscription billing currency, but it must not format merchant transactions.

Current live data has 16 Shops:

- 13 have no Shop currency;
- 12 have no Shop country;
- only 3 have KES saved explicitly.

Current field metadata is incorrect:

- Product `price` and `selling_price` use `options = "shop:currency"`.
- Frappe 16 expects a linked currency reference in the three-part form `DocType:link_field:currency_field`, such as `Shop:shop:currency`.
- The current two-part value is ignored and Frappe falls back to the system currency.
- Sale Invoice `total` has no currency option or currency field.
- Tookio Purchase `amount` has no currency option or currency field.
- The Sale Invoice child price also uses `shop:currency`, even though the child row has no `shop` field.
- Eight dashboard charts and four monetary Number Cards hard-code `KES`.
- Current reports can sum values from different Shops without guarding against mixed currencies.

## 3. Target subscription model

Use one canonical plan catalog everywhere: database, pricing page, subscription page, checkout, emails, and mobile API. Pages must read plan records instead of keeping their own hard-coded names, prices, and features.

### 3.1 Target tiers

| Tier | Shops | Products | Sale invoices | Published storefronts | Purpose |
| --- | ---: | ---: | ---: | ---: | --- |
| Free | 1 | 50 | 200 | 0 | Stock, sales, and expense tracking |
| Starter | 1 | 150 | Unlimited | 1 | One business and one public storefront |
| Pro | Unlimited | Unlimited | Unlimited | 1 | Many Shops, with one selected Shop published |
| Premium | Unlimited | Unlimited | Unlimited | Unlimited | Publish a storefront for every owned Shop |

Premium pricing is a business decision and should remain configurable rather than hard-coded. The suggested data migration is:

1. Rename the current database `Premium Plan` to `Pro Plan`. Frappe's document rename must update existing User Subscription links.
2. Keep the current KES 1,160 price for Pro so it aligns with the existing `$9` marketing tier.
3. Create a new Premium Plan with a configurable price.
4. Update Free and Starter to the runtime limits above, avoiding an accidental reduction for existing users.
5. Render all plan prices with each plan record's own billing currency. Merchant Shop currency does not change Tookio subscription billing currency.

### 3.2 New entitlement fields

Add stable, non-label identifiers and storefront capabilities to `Tookio Subscription`:

- `plan_code`: unique, immutable values `free`, `starter`, `pro`, `premium`;
- `storefront_enabled`: Check;
- `storefront_limit`: Int, where `0` means unlimited only when `storefront_enabled = 1`;
- optional future `custom_domain_enabled`: Check.

Do not determine paid access with `current_subscription != "Free Plan"`. Resolve the active plan by `plan_code` and explicit capabilities.

Plan records should be authoritative. If Tookio needs grandfathered limits, model them as explicit per-subscription overrides rather than stale copied fields that silently disagree with the plan.

Count entitlements by owner:

```text
Shop usage       = count Shop where owner = user
Product usage    = count Product where owner = user
Invoice usage    = count Sale Invoice where owner = user
Storefront usage = count published Storefront where owner = user
```

Refactor limit hooks to use the validated document owner, not blindly `frappe.session.user`. This is required for a Guest checkout endpoint that creates a draft invoice owned by the Shop owner.

## 4. Correct multi-Shop, multi-country, and multi-currency model

### 4.1 Scope

MVP supports one pricing/transaction currency per Shop, with different Shops in the same Frappe site using different currencies. It does not perform FX conversion.

Example:

```text
User A
├── Nairobi Shop — KES
├── Export Shop — USD
└── Kampala Shop — UGX
```

Products and documents linked to Nairobi Shop display KES; those linked to Export Shop display USD. No code may pick one of these Shops as the user's currency source.

### 4.2 Shop fields and behavior

- Make `Shop.country` required for all new Shops.
- Make `Shop.currency` required for all new Shops.
- When country is selected during Shop creation, suggest that country's common currency, but let the seller override it before saving.
- A country suggestion must never mutate another Shop or a global Frappe default.
- Normalize the Shop WhatsApp number to E.164 using the Shop country.
- Keep subscription billing currency independent from Shop currency.

Backfill legacy Shops through a migration report/wizard. Do not guess currency for the 13 legacy Shops and silently reinterpret their prices. Ask each owner to confirm country and currency; KES can be a preselected suggestion for Kenyan Shops.

After a Shop has Products or financial documents, lock direct currency edits for MVP. A later “Change Shop Currency” wizard can require explicit new prices and preserve historical documents. Do not automatically FX-convert historical amounts.

### 4.3 Currency snapshots

Add a read-only `currency` Link to Currency on these records:

- Product;
- Sale Invoice;
- Tookio Purchase;
- future payment/order records that store money.

On every validate, fetch currency from the record's exact Shop after validating ownership:

```python
shop = get_owned_shop(doc.shop, doc.owner)
doc.currency = shop.currency
```

Use each record's direct currency field for formatting:

- Product `price.options = "currency"`
- Product `selling_price.options = "currency"`
- Sale Invoice `total.options = "currency"`
- Tookio Purchase `amount.options = "currency"`
- Sale Invoice child `price.options = "currency"`; Frappe can resolve it from the parent Sale Invoice.

`Shop:shop:currency` is the correct three-part Frappe syntax and is acceptable for a simple linked field, but direct currency snapshots are safer for list views, permission boundaries, historical transactions, and reports. Server validation remains authoritative in either case.

### 4.4 Reports and dashboards

Every monetary query must include Shop and currency.

- A single-Shop report uses that exact Shop's currency.
- A multi-Shop report may total rows only when all included Shops share one currency.
- If currencies differ, group totals by currency or require the seller to choose a Shop.
- Never produce a grand total such as `KES + USD`.
- Remove hard-coded KES from Tookio dashboard charts and Number Cards.
- Replace generic monetary Number Cards with a Shop-filtered API/card that returns `{value, currency}`.
- Include a currency field on report rows and set Currency column options to that field.

An optional explicit “Shop” selector can remember the seller's last choice in the UI. It is a filter only. It must never change how an existing record's currency is resolved.

## 5. Storefront data model

Create a `Tookio Storefront` DocType, one published storefront per Shop.

Core fields:

- `shop`: required unique Link to Shop;
- `slug`: required unique normalized slug;
- `published`: Check;
- `display_name`: fetched/defaulted from Shop name;
- `hero_title`, `hero_text`;
- `theme_color` and a small supported theme preset;
- `whatsapp_number`: optional override, otherwise Shop mobile number;
- `show_address`, `show_stock`, `show_whatsapp_order`;
- `seo_description`;
- optional `custom_domain` reserved for a later phase.

The Storefront `owner` must equal the linked Shop's owner. Validate that invariant on every save. Publishing must call the entitlement service and count the owner's already published storefronts.

Add only the minimum Product website fields:

- `website_published`;
- optional `website_featured`;
- optional `website_sort_order`.

The slug is initially derived from the Shop name: `My Shop` becomes `my-shop.tookio.shop`. Save it as its own value so renaming a Shop does not unexpectedly break links. Reject reserved slugs such as `www`, `app`, `api`, `admin`, `login`, `assets`, and `mail`. Handle collisions with a clear user choice or suffix.

## 6. Storefront UI

Build a Vue 3 SPA with Frappe UI and its Tailwind semantic tokens. The current app has no Frappe UI frontend build, so add a small Vite frontend inside the app and publish its built assets through Frappe.

Borrow the information architecture of Frappe Webshop—catalog, product detail, cart, and checkout—but use Frappe UI components consistently. Do not copy Webshop's account-required cart behavior; Tookio's MVP cart is guest-first.

Mobile-first pages:

1. Home: Shop logo/name, short hero, featured products, address/location, WhatsApp button.
2. Products: compact two-column mobile grid, image, name, formatted price, and stock state.
3. Product detail: image, name, price, availability, quantity, add to cart.
4. Cart drawer/page: quantities, line totals, total, remove/edit controls.
5. Checkout: customer name, phone, delivery/pickup location, order summary, “Order via WhatsApp”.
6. Confirmation: Tookio order number and a second button if WhatsApp did not open.

Keep the cart in local storage, namespaced by storefront slug. Never allow products from different Shops in one cart.

The seller sidebar gets a simple “Website” section:

- Overview and public URL;
- Publish/unpublish;
- Appearance and homepage copy;
- Products shown online;
- Contact, WhatsApp, address, and location visibility;
- Orders linking to storefront-created draft Sale Invoices.

## 7. Public API and WhatsApp order flow

### 7.1 Read APIs

Resolve request host to one published `Tookio Storefront`, then to its exact Shop. Return only explicit public fields.

- `get_storefront()`
- `list_storefront_products(search, page)`
- `get_storefront_product(product_name)`

All Product queries must include both `shop = storefront.shop` and `enabled = 1` and `website_published = 1`.

Do not expose generic `frappe.client.get_list` to Guest or use broad `ignore_permissions` queries.

### 7.2 Checkout API

`place_whatsapp_order(storefront, cart, customer)` performs all of the following on the server:

1. Resolve storefront host/slug to one published Storefront and exact Shop.
2. Re-read each Product by name with the same exact Shop filter.
3. Reject disabled, unpublished, mismatched-Shop, or unavailable Products.
4. Ignore client prices, totals, currency, and Shop; calculate all of them from server records.
5. Recheck stock without reserving it.
6. Create a Draft Sale Invoice owned by `shop.owner`, with `shop`, currency snapshot, customer details, and source `Storefront WhatsApp`.
7. Save a public idempotency token so retries do not create duplicate drafts.
8. Return the draft order number and a `wa.me` URL.

The WhatsApp message should include Shop name, Tookio order number, line items, quantities, total with currency code, customer name, phone, and delivery/pickup note.

Creating the draft tracks demand but does not reduce stock. The merchant reviews it and submits the Sale Invoice when the order is confirmed; the existing submit flow then records the stock transaction. A cancelled WhatsApp enquiry remains a cancelled/deleted draft and never affects stock.

Add rate limiting, request-size limits, a honeypot, and server logging to the Guest checkout endpoint.

## 8. Wildcard domain and Frappe/Nginx design

Use one Frappe site for all Shops.

### 8.1 DNS and TLS

- `tookio.shop` and the canonical admin/marketing host point to the Tookio server.
- `*.tookio.shop` points to the same server.
- Install a certificate covering `tookio.shop` and `*.tookio.shop` using DNS-01 validation.

### 8.2 Nginx/Frappe routing

The wildcard Nginx server block accepts `*.tookio.shop` and proxies it to the same Frappe upstream. It must preserve the original `Host` for storefront resolution while forcing `X-Frappe-Site-Name` to the actual Frappe site name. If Nginx sends the subdomain itself as `X-Frappe-Site-Name`, Frappe will try to find a separate site directory for every Shop, which is the wrong architecture.

Conceptually:

```nginx
server_name tookio.shop *.tookio.shop;
proxy_set_header Host $host;
proxy_set_header X-Frappe-Site-Name actual-frappe-site-name;
```

Keep this customization in a maintained Nginx include/template so a future `bench setup nginx` does not erase it.

Use Frappe's `website_path_resolver` hook to inspect the request host. On a Storefront host, resolve `/` and SPA routes to the Storefront shell; on the canonical Tookio host, call Frappe's normal path resolver. Static assets and `/api` remain normal Frappe routes.

Cache Storefront responses by host plus path, never by path alone. Invalidate Storefront/Product caches after relevant updates.

For local development, support `/store/<slug>` and tests with an explicit `Host` header; production redirects that fallback route to the canonical subdomain.

## 9. Signup password email

The attached email is generated by Frappe `User.set_new_password()` when an existing User's `new_password` is saved. The current custom signup completion deliberately sets `user.flags.in_insert = True`, which takes Frappe's initial-password path and suppresses that security alert.

The current HEAD also globally overrides `User.set_new_password()` and monkey-patches the base class to suppress the alert for every password change. That is broader than signup and removes a real security warning for genuine later password changes.

Preferred implementation:

- keep the alert for genuine logged-in password changes and resets;
- suppress it only inside `complete_mobile_signup` by using the explicit initial-password path;
- add an automated test asserting one verification email is sent, the password is usable, and no security-alert email is queued;
- remove the global monkey-patch after that scoped test passes.

If the business decision is to suppress the security email globally, keep the override but document the security trade-off and test both signup and normal password changes. The production email supplied was sent on 2026-07-29; the newest global suppression commit is dated 2026-08-11, so deployment/restart state must be verified before assuming production has the fix.

## 10. Delivery phases for Terra

### Phase 0: characterization tests

- Tests for owner-only Shop access and multi-Shop ownership.
- Tests proving Product/Invoice/Purchase currencies come from their exact Shop.
- Tests for mixed-currency reporting behavior.
- Tests capturing current plan enforcement and signup email behavior.

### Phase 1: tenancy and currency foundation

- Add server-side Shop ownership helper and relational validations.
- Remove unrestricted Product read permission.
- Add currency snapshot fields and correct Currency options.
- Backfill/confirmation workflow for legacy Shop country/currency.
- Replace hard-coded KES dashboards/cards.
- Make mixed-currency reports safe.

Do not begin public checkout until this phase passes.

### Phase 2: normalize subscriptions

- Add `plan_code` and storefront entitlement fields.
- Reconcile Free/Starter limits.
- Rename database Premium to Pro and create the new Premium tier.
- Replace hard-coded website pricing catalogs with database plans.
- Implement a real daily expiration job.
- Centralize all entitlement checks in one service.

### Phase 3: Storefront backend

- Add Storefront DocType and Product publishing fields.
- Add owner-only seller APIs and scoped Guest catalog APIs.
- Implement host resolver and `/store/<slug>` development fallback.
- Implement draft Sale Invoice checkout and WhatsApp URL generation.

### Phase 4: Frappe UI frontend

- Create Vite/Vue 3/Frappe UI frontend.
- Build mobile home, catalog, product, cart, checkout, and confirmation.
- Build the seller Website sidebar/settings pages.
- Add empty, loading, out-of-stock, offline, and failure states.

### Phase 5: infrastructure and rollout

- Configure wildcard DNS, wildcard TLS, and fixed Frappe site routing in Nginx.
- Deploy behind a feature flag.
- Enable Tookio staff test Shops first, then Starter/Pro, then Premium multi-storefront.
- Monitor Guest API errors, draft-order duplication, WhatsApp conversion, and subscription denials.

### Phase 6: later work, not MVP

- Paystack checkout and split settlements;
- custom merchant-owned domains;
- shipping integrations and delivery pricing;
- stock reservation/expiry;
- FX conversion and consolidated base-currency accounting;
- customer accounts, saved addresses, and order tracking portal.

## 11. Acceptance criteria

- One user can own a KES Shop and a USD Shop; every screen and saved record displays the correct linked-Shop currency.
- Opening or creating records for one Shop never changes formatting for another Shop.
- No code path calls `get_last_doc("Shop")`, orders Shops by creation to choose context, or uses system KES for merchant money.
- A seller cannot link their Product, Invoice, Purchase, or Storefront to another seller's Shop, even with a crafted API request.
- Free cannot publish a website; Starter can publish one; Pro can own unlimited Shops but publish one; Premium can publish one per owned Shop.
- `my-shop.tookio.shop` resolves to the one Storefront record for `my-shop` inside the same Frappe site.
- Guest checkout cannot choose price, currency, Shop, or record owner.
- Checkout creates one idempotent Draft Sale Invoice, opens WhatsApp, and does not reduce stock until merchant submission.
- Mixed KES/USD reports never display a false combined total.
- Signup sends the intended verification email and no follow-up security alert; the chosen behavior for genuine password changes is tested explicitly.

## 12. Research references

- [Frappe UI](https://github.com/frappe/frappe-ui): Vue 3, Tailwind, components, and Frappe data utilities.
- [Frappe Webshop](https://github.com/frappe/webshop): catalog/cart/checkout information architecture to borrow selectively.
- [Frappe DNS multitenancy](https://docs.frappe.io/framework/user/en/bench/guides/setup-multitenancy): useful background, but Tookio storefronts remain records in one Frappe site.
- [Frappe custom domains](https://docs.frappe.io/framework/v15/user/en/bench/guides/adding-custom-domains): domain and TLS behavior for a Frappe site.
- [Uzanga](https://uzanga.com/): relevant Kenyan pattern—each business has a separate storefront, guest self-service checkout, local delivery/payment concepts, and WhatsApp/Instagram integration. Tookio's MVP differentiator is direct linkage to existing Shop stock, sales, expenses, and draft invoices.
