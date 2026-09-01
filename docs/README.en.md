# Neuromedia — AI Marketplace

[Русский](../README.md) · [Catalog](../content/catalog/catalog.en.json) · [Website](https://neuromedia.cloud/)

**Neuromedia** is an AI marketplace for business-ready solutions, agents, APIs, and infrastructure. It helps teams select practical AI tools and services for sales, support, content, documents, automation, and production deployment.

> This is a public project showcase, not the marketplace source code. The live assortment and checkout are available at [neuromedia.cloud](https://neuromedia.cloud/).

## What the marketplace offers

- **AI APIs and models** for products, bots, CRM, and internal services.
- **AI agents** for sales, customer support, content, and operations.
- **Automation** workflows for leads, documents, spreadsheets, CRM, and back office.
- **Media generation** for image, video, and AI content workflows.
- **AI infrastructure** for inference, compute, and production workloads.
- **Professional services** for implementation, setup, and adaptation to business needs.

## How it works

1. Select a direction or solution in the [live catalog](https://neuromedia.cloud/).
2. Review the description, delivery format, current price, and availability.
3. Place an order on the website; **cryptocurrency payments** are available for supported checkout flows.
4. Receive digital access, a service, or delivery support under the selected offer’s terms.

## Content and updates

Beyond the catalog, Neuromedia publishes **articles, guides, news, and cases** about applied AI. The marketplace evolves to make AI APIs, agents, automation, and infrastructure easier to evaluate.

## Public catalog

A machine-readable public catalog snapshot is maintained in:

- [Russian catalog](../content/catalog/catalog.ru.json)
- [English catalog](../content/catalog/catalog.en.json)
- [Synchronization policy and schema](synchronization.md)

These files intentionally exclude marketplace source code, supplier links, keys, customer data, private inventory, and infrastructure configuration. Repository prices and availability are informational; always confirm the live product page before payment.

## Synchronization

The repository is prepared for scheduled updates of categories, public product data, prices, and statuses. Its synchronization script consumes **only a purpose-built public JSON export** and validates the schema, source domain, and secret-free content before it can create a commit.

See [docs/synchronization.md](synchronization.md).

---

© Neuromedia. Product names, prices, availability, and terms may change. The live website is the authoritative source.
