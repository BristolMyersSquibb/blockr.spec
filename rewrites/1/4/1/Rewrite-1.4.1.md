# Model access: providers, gateways and credentials
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): where the assistant's calls to a model go, how they are authenticated, who picks the model, and the blockr options through which a deployment sets all three.
It shapes the Work items of that part that send the calls and authenticate them, while the loop, its tools and its state stay with the part.

## What must hold

1. A deployment chooses where the assistant's calls go, how they are authenticated and which models it offers through its blockr options alone, without changing any code of the assistant.
2. A demo works for visitors who have no account with any provider or gateway.
3. No call to a model goes through the session's R process.
4. A visitor's own key never reaches the board, a saved board or R.

## Today

Today's assistant calls its model from the session's R process, through the ellmer chat that the blockr option `chat_function` gives, with whatever credential that function reads in R's environment ([Assistant as a plugin](Rewrite-1.4#today)).
Both apps that use it chat with OpenAI, with a key in `OPENAI_API_KEY`.

## Proposal

### Where the calls go

From the browser, a provider, a gateway and a company's own proxy look alike: each is a base URL that speaks one provider's API and takes a credential.
So the assistant reaches all three in one way, through the providers of its library, which take the base URL: `baseURL` in the AI SDK's providers, and `baseUrl` in a provider that pi's `createProvider()` makes (notes).
The places include:

- A provider, such as OpenAI or Anthropic.
- A gateway, such as OpenRouter or Vercel's AI Gateway, which reaches the models of many providers through one API and one account.
- A company's own proxy, which holds the provider's key inside the company's network and decides who may call.

The assistant speaks OpenAI's Responses and Chat Completions APIs and Anthropic's Messages API, all three of which Vercel's AI Gateway speaks, while OpenRouter serves Chat Completions and Anthropic's Messages (notes), so a place that speaks one of them takes configuration alone (condition 1).
A company's own proxy is a place like a gateway, which the company runs beside the app, so it needs nothing more here.

A deployment sends every call to one place.
Today a `chat_function` list may mix providers, each entry with a credential of its own (Who picks the model), which a gateway gives after the switch, through one place and one key.
Several places in one deployment are later work, which nothing here rules out.

No call goes through the session's R process (condition 3).
R runs one request at a time ([Wire protocol](Rewrite-1.1.9#one-request-at-a-time)), so a model call there would hold up evaluation for its whole length, and httpuv cannot stream a response (notes).
A key held in R is also safe from no visitor who runs R through a block that takes code, as the next section has it.

### How a call is authenticated

The loop takes its credential through one function that the library calls for each request, a `fetch` of its own in an AI SDK provider and `getApiKey` in pi, so that each way below feeds it and the loop knows none of them ([Assistant as a plugin](Rewrite-1.4#proposal)).
None of these ways suits every deployment, and which one a call takes follows from the blockr options (The blockr options):

| Way | The hoster provides | A visitor needs | Who pays | What a visitor can copy |
|---|---|---|---|---|
| The deployment's key | A key, in the blockr option `assistant_api_key`, which the plugin reads through `CoreApi.blockrOption()` | Nothing | The hoster | The hoster's key, which works until the hoster revokes it |
| The visitor's own key | Nothing | A key of their own, which they trust the app with | The visitor | Their own key, and nothing of the hoster's |
| A login with a service that offers one, such as OpenRouter | An app that sends the visitor to the service's login | An account with that service | The visitor | A key on their own account, which works until they revoke it, since the login sets no expiry (notes) |
| The hosting platform's integration, such as Connect's | Later | Later | Later | Later |

Where the deployment sets a key, every call uses it, and the chat asks for nothing.
Otherwise the chat asks the visitor for their own key, and offers a login beside it where the place offers one, as OpenRouter does.
So no blockr option lists the ways, and the hosting platform's integration, once it comes, will follow from the platform that the app runs on.

- The deployment's key is the easiest way and the least safe.
  Any visitor who can use the assistant can take it, today as after the switch, since a visitor runs R through a block that takes their code, as core's subset block takes its `subset` and `select` ([R/transform-subset.R#L29-L31](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-subset.R#L29-L31)), and through the assistant's request that runs the R its model writes ([Assistant as a plugin](Rewrite-1.4#proposal)).
  A key in the browser only makes that visible.
  Limiting it stays the deployment's job ([State in JS](Rewrite-1#proposal)), which matters most for an app on the public internet, whose visitors are anyone.
  It suits a demo, whose visitors need no account (condition 2).
  The plugin reads it only from `assistant_api_key`, never from a variable that a provider's own clients read, such as the `OPENAI_API_KEY` that ellmer reads in R, so that a key set for code in R reaches no browser unless the deployment hands it over.
- The visitor's own key stays in the page's memory: the visitor types it into the assistant's panel, and the plugin hands it to the library for each call.
  It stays out of a board option, whose value the board saves once someone sets it ([Board options and blockr options](Rewrite-1.1.13#the-two-kinds)), and out of browser storage that outlives the page, which every page served from the same origin can read (condition 4).
  So the visitor types the key again after each reload.
- A login works only with a service that offers one to a web page: OpenRouter does, OpenAI offers its own to selected partners for now, and Anthropic forbids one (notes).
  Every visitor then needs an account with that service, which a demo cannot ask of its visitors.
  The key that a login gives is the visitor's own, so it stays in the page's memory, as a typed key does, and a reload asks for the login again.
  OpenRouter's login can also make its key in a workspace of the hoster's, through `required_workspace_id`, and OpenRouter bills an organization's keys to the organization's credits (notes), which would let a company pay for the calls of its members, each logging in with an account in its organization.
  That is later work, which nothing here rules out.
- The hosting platform's integration is later work, for which this page leaves room.
  The platform vouches for the visitor or for the deployment, as Connect's OAuth integrations give R a visitor's token for some providers (notes), so that the app holds no key of the hoster's.

### Who picks the model

Today the blockr option `chat_function` gives one of ellmer's chat functions, which fixes the model, or a named list of them ([Assistant as a plugin](Rewrite-1.4#today)).
From a list, the user picks one through core's board option `llm_model`, which the dock's options sidebar shows, and the board saves the pick by its name.
CEDX's script offers three of OpenAI's models that way, named by their ids, while blockr.uat's chats with ellmer's default.
Both options go, since they were shaped for ellmer's chat functions ([Assistant as a plugin](Rewrite-1.4#proposal)), while what they let a deployment choose carries over.

The models that a deployment offers are those it names in `assistant_models`, the first being the default (The blockr options):

- One model fixes the model for every board, and the chat offers no pick.
- Several let the user pick one in the chat, and the first serves until someone does.
- Where the deployment names none, the chat offers the models that the place lists for the key, keeping those that take tools where the list says which do, with no default, so that the chat asks for a pick before the first turn.

No list says which model to start with, and CEDX's script warns that a `chat_function` left unset gives ellmer's default "silently" ([dev/cedx/app.R#L66-L71](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/app.R#L66-L71)), which a pick that the chat asks for avoids.
OpenAI's list says nothing of what a model takes, so the issue that sends the calls settles how the plugin keeps the models that take tools from it, such as by their ids (notes).
A call to a model that the visitor's account cannot reach fails as any call does ([The assistant's chat](Rewrite-1.4.4#what-fails)).

Who pays for the calls decides where a pick is kept, so that no blockr option sets it:

- With the deployment's key, the board keeps the pick, since every visitor reaches the same models at the hoster's cost, as each of CEDX's boards keeps its pick today.
  The pick is a setting of the assistant's own, so it goes in the assistant's state rather than in a board option, which is meant for how the board is shown ([Places the dock offers plugins](Rewrite-1.2.4#settings)), and a command of the assistant's sets it, which undo leaves alone, as it leaves a board option's value ([The assistant's state](Rewrite-1.4.3#commands)).
  Where the deployment does not offer the board's pick, the chat says so and talks to the default, or asks for a pick where the deployment names no models, while the state keeps the pick until someone picks another, so that the board talks to its model again where that model is offered.
- With the visitor's own key or a login, the visitor's browser keeps the pick, since the next visitor of the board may have another account, which reaches other models.
  A model's name gives nothing away, unlike a key, so the pick stays in the browser's local storage, under the plugin class's id, and outlives a reload, while a pick there that the deployment does not offer, such as one made in another app served from the same origin, gives way to the default.
  The board's pick stays in the state, unread.

The chat's footer offers the pick in both cases ([The assistant's chat](Rewrite-1.4.4#the-model)).

### The blockr options

A deployment sets all of this through four blockr options, each a string that an environment variable can give, so that a deployment such as Connect sets them without touching the app script ([Board options and blockr options](Rewrite-1.1.13#blockr-options)):

| Blockr option | What it holds | Where it is unset |
|---|---|---|
| `assistant_base_url` | The place's base URL | OpenAI's API, which today's default chat function calls |
| `assistant_api` | The API that the place speaks: `"openai"` for OpenAI's Responses API, `"openai_chat"` for its Chat Completions API, or `"anthropic"` for Anthropic's Messages API | The one that the plugin knows the place to speak, for OpenAI, Anthropic, OpenRouter and Vercel's AI Gateway, while any other place, such as a company's own proxy, sets it |
| `assistant_api_key` | The deployment's key | None, so that the visitor authenticates (How a call is authenticated) |
| `assistant_models` | The models offered, the first being the default, separated by commas in an environment variable | None, so that the chat offers the models that the place lists for the key (Who picks the model) |

A demo on OpenAI's models then sets two, `BLOCKR_ASSISTANT_API_KEY` and, say, `BLOCKR_ASSISTANT_MODELS=gpt-5.4`, and an app for visitors who log in with OpenRouter sets one, `BLOCKR_ASSISTANT_BASE_URL=https://openrouter.ai/api/v1`.
The plugin reads them through `CoreApi.blockrOption()`, which asks R for them, and takes `assistant_models` as an array from an R option, or splits it at its commas from an environment variable, since each reader converts what it reads ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).

## Open questions

- Whether OpenAI's API lets a page read its responses: it allows a page's preflight, but its 401s carry no `Access-Control-Allow-Origin` ([Assistant as a plugin](Rewrite-1.4)).
  It blocks no Work item, since a deployment whose visitors cannot call OpenAI from a page reaches its models through a gateway, and a call from a page with a real key settles it.
- Whether a company's network lets visitors' browsers reach the place the calls go, as BMS's network may not let them reach api.openai.com.
  It blocks no Work item, since a company's own proxy is a place like any other, and each such deployment settles it as it is set up.

<details><summary>Notes for implementers</summary>

Read on 2026-11-12:

- Anthropic: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, Max, or Ultra plan credentials on behalf of their users", and developers "should use API key authentication through Claude Console or a supported cloud provider" ([Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)).
  A key that a customer provisions "for use by the customer's own authorized users" stays allowed, "provided the resulting usage is billed to the key owner" (same page).
- OpenAI: Sign in with ChatGPT is an "OAuth 2.0 Authorization Code flow with PKCE and OpenID Connect", "currently available to selected commercial partners through a limited trial", whose guide for websites calls the token endpoint "from your backend" ([On your website](https://developers.openai.com/siwc/website)).
  Its plan usage, for "eligible Responses API requests", is documented for "open-source and locally hosted apps", with an interest form for "a paid or remotely hosted app" ([plan usage](https://developers.openai.com/siwc/token-sharing-open-source)).
- OpenRouter: its OAuth login with PKCE gives the app "an API key tied to their account", whose requests "are billed to their own OpenRouter credits", and `required_workspace_id` "Requires the new API key to be created in this workspace", which the visitor must be able to reach ([OAuth PKCE](https://openrouter.ai/docs/use-cases/oauth-pkce)).
  Its login's parameters are `callback_url`, `code_challenge`, `code_challenge_method`, `key_label`, `workspace_id`, `required_workspace_id` and `state`, none of which sets a limit or an expiry (same page).
- Vercel's AI Gateway: "Every request to AI Gateway requires Vercel authentication.
  Use an AI Gateway API key or OpenID Connect (OIDC) token."
  "Vercel deployments receive an OIDC token as `VERCEL_OIDC_TOKEN`", while an API key does not expire "unless you set an expiration date when you create them or you revoke them", and may carry a budget.
  It takes OpenAI's Chat Completions and Responses APIs and Anthropic's Messages API ([Authentication and BYOK](https://vercel.com/docs/ai-gateway/authentication-and-byok)).

Read on 2026-11-13:

- Anthropic's `GET /v1/models` shows "which models are available for use in the API", the most recently released first, each with its `capabilities`, `display_name`, `lifecycle` and `line`, the active and deprecated models by default ([List Models](https://platform.claude.com/docs/en/api/models/list)).
- OpenAI's `GET /v1/models` "Lists the currently available models", each with `id`, `created`, `owned_by` and `shutdown_date`, and nothing of what a model takes ([List models](https://developers.openai.com/api/reference/resources/models/methods/list)).
- OpenRouter's `GET /api/v1/models` takes a key, filters by `supported_parameters`, among whose values are `tools` and `tool_choice`, and sorts by `newest`, while each model names in `endpoints` the paths that serve it, such as `/api/v1/chat/completions` and `/api/v1/messages` ([List models](https://openrouter.ai/docs/api-reference/models/get-models)).
- Vercel's `GET https://ai-gateway.vercel.sh/v1/models` "requires no authentication", gives each model's `type`, such as `language` or `embedding`, and names models as `creator/model-name` ([Models and providers](https://vercel.com/docs/ai-gateway/models-and-providers)).
- OpenRouter: "API usage from any organization key is billed to the organization's credit pool" ([Organization management](https://openrouter.ai/docs/cookbook/administration/organization-management)).
  A key's `limit` is "the spend limit in USD, or `null` if the key has no limit", and its `expires_at` is null "if the key never expires", while "An expiration can't be added to an existing key" ([API key audit](https://openrouter.ai/docs/cookbook/administration/api-key-audit)).

The AI SDK's providers take `baseURL`, `headers` and `fetch` ([Anthropic provider](https://ai-sdk.dev/providers/ai-sdk-providers/anthropic)), and pi reaches a place that speaks a provider's API as a provider that `createProvider()` makes, whose models name the place as their `baseUrl` ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#createprovider)).
The `streamProxy()` of pi posts to a server of pi's own at `/api/stream`, which answers in pi's events ([proxy.ts#L146-L150](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/src/proxy.ts#L146-L150)), so a company's proxy that passes a provider's API through is reached through `createProvider()` instead.
Both official SDKs refuse to run in a browser without `dangerouslyAllowBrowser: true`, a key there being readable by every visitor.

Calls from the browser leave from the visitor's machine, where a company network may block the provider's domain or buffer the stream, and an endpoint private to the server's network is out of reach, as is a provider that refuses cross-origin requests, which is what a company's own proxy is for.
A proxy in R, which forwards the provider's own API with the credential added, cannot stream over HTTP, since httpuv takes a response body only whole, as "A string (or raw vector)", so streamed tokens would travel over the websocket and pause while R evaluates.

Connect's viewer OAuth integrations, such as for Azure, AWS and Databricks, give R a visitor's access token through `connectapi::get_oauth_credentials()` and the session's `Posit-Connect-User-Session-Token` header, and "OAuth refresh tokens are never returned by Connect" ([Connect](https://docs.posit.co/connect/user/oauth-integrations/)).
Anthropic's Workload Identity Federation exchanges a JWT from an identity provider, such as Entra ID, for a Claude token that acts as a service account and lasts 60 seconds to 24 hours, one hour by default ([docs](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)), which a visitor who runs R can mint as well, so it limits how long a copy works rather than who can get one.
OpenAI's and Gemini's short-lived tokens are made for their realtime and live APIs ([OpenAI](https://developers.openai.com/api/docs/guides/realtime-webrtc), [Gemini](https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens)).

</details>
