# Model access: providers, gateways and credentials
Status: draft. Design for [Assistant as a client extension](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a client extension](Rewrite-1.4)): where the assistant's calls to a model go, how they are authenticated, and who picks the model.
It shapes the Work items of that part that send the calls and authenticate them, while the loop, its tools and its state stay with the part.

## What must hold

1. A deployment chooses where the assistant's calls go and how they are authenticated through its configuration alone, without changing any code of the assistant.
2. A demo works for visitors who have no account with any provider or gateway.
3. No call to a model goes through the session's R process.
4. A visitor's own key never reaches the board, a saved board or R.

## Today

Today's assistant calls its model from the session's R process, through the ellmer chat that the blockr option `chat_function` gives, with whatever credential that function reads in R's environment ([Assistant as a client extension](Rewrite-1.4#today)).
Both apps that use it chat with OpenAI, with a key in `OPENAI_API_KEY`.

## Proposal

### Where the calls go

From the browser, a provider, a gateway and a company's own proxy look alike: each is a base URL that speaks one provider's API and takes a credential.
So the assistant reaches all three in one way, through the providers of its library, which take the base URL: `baseURL` in the AI SDK's providers, and `baseUrl` in a provider that pi's `createProvider()` makes (notes).
The places include:

- A provider, such as OpenAI or Anthropic.
- A gateway, such as OpenRouter or Vercel's AI Gateway, which reaches the models of many providers through one API and one account.
- A company's own proxy, which holds the provider's key inside the company's network and decides who may call.

The assistant speaks OpenAI's API and Anthropic's, both of which Vercel's AI Gateway speaks too (notes), so a place that speaks either takes configuration alone (condition 1).
A company's own proxy is a place like a gateway, which the company runs beside the app, so it needs nothing more here.

No call goes through the session's R process (condition 3).
R runs one request at a time ([Wire protocol](Rewrite-1.1.9#one-request-at-a-time)), so a model call there would hold up evaluation for its whole length, and httpuv cannot stream a response (notes).
A key held in R is also safe from no visitor who runs R through a block that takes code, as the next section has it.

### How a call is authenticated

The loop takes its credential through one function that the library calls for each request, a `fetch` of its own in an AI SDK provider and `getApiKey` in pi, so that each way below feeds it and the loop knows none of them ([Assistant as a client extension](Rewrite-1.4#proposal)).
A deployment offers one of these ways or several, since none suits every deployment:

| Way | The hoster provides | A visitor needs | Who pays | What a visitor can copy |
|---|---|---|---|---|
| The deployment's key | A key, in a blockr option that the plugin reads through `CoreApi.blockrOption()` | Nothing | The hoster | The hoster's key, which works until the hoster revokes it |
| The visitor's own key | Nothing | A key of their own, which they trust the app with | The visitor | Their own key, and nothing of the hoster's |
| A login with a service that offers one, such as OpenRouter | An app that sends the visitor to the service's login | An account with that service | The visitor, or the hoster where the key is made in a workspace of the hoster's (Open questions) | A key on their own account |
| The hosting platform's integration, such as Connect's | Later | Later | Later | Later |

- The deployment's key is the easiest way and the least safe.
  Any visitor who can use the assistant can take it, today as after the switch, since a visitor runs R through a block that takes their code, as core's subset block takes its `subset` and `select` ([R/transform-subset.R#L29-L31](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-subset.R#L29-L31)), and through the assistant's request that runs the R its model writes ([Assistant as a client extension](Rewrite-1.4#proposal)).
  A key in the browser only makes that visible.
  Limiting it stays the deployment's job ([State in JS](Rewrite-1#proposal)), which matters most for an app on the public internet, whose visitors are anyone.
  It suits a demo, whose visitors need no account (condition 2).
- The visitor's own key stays in the page's memory: the visitor types it into the assistant's panel, and the plugin hands it to the library for each call.
  It stays out of a board option, whose value the board saves once someone sets it ([Board options and blockr options](Rewrite-1.1.13#the-two-kinds)), and out of browser storage that outlives the page, which every page served from the same origin can read (condition 4).
  So the visitor types the key again after each reload.
- A login works only with a service that offers one to a web page: OpenRouter does, OpenAI offers its own to selected partners for now, and Anthropic forbids one (notes).
  Every visitor then needs an account with that service, which a demo cannot ask of its visitors.
- The hosting platform's integration is later work, for which this page leaves room.
  The platform vouches for the visitor or for the deployment, as Connect's OAuth integrations give R a visitor's token for some providers (notes), so that the app holds no key of the hoster's.

### Who picks the model

Today's board option `llm_model` and blockr option `chat_function` go, since both were shaped for ellmer's chat functions ([Assistant as a client extension](Rewrite-1.4#proposal)).
Whether the deployment alone picks the model, or the user picks it in the chat, is open (Open questions).

## Open questions

- How a deployment sets where the calls go, which ways to authenticate it offers and which models: through which blockr options, under which names and in which shapes.
  It blocks the Work items that send the calls and authenticate them, and agreeing the options settles it.
- Who picks the model: the deployment alone, or the user in the chat from the models that the place offers, and whether the user's pick is saved with the board, in the assistant's state, or kept for the visitor's page alone.
  It blocks the schema of the assistant's state, and weighing a board that opens with the model its author picked against a visitor whose own key reaches other models settles it.
- Whether a key that OpenRouter's login makes in a workspace of the hoster's bills that workspace, and whether such a key can carry a limit or an expiry date.
  It blocks the login's row in the table, and OpenRouter's docs on workspaces settle it.
- Whether a company's network lets visitors' browsers reach the place the calls go, as BMS's network may not let them reach api.openai.com.
  It blocks no Work item, since a company's own proxy is a place like any other, and each such deployment settles it as it is set up.

<details><summary>Notes for implementers</summary>

Read on 2026-11-12:

- Anthropic: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, Max, or Ultra plan credentials on behalf of their users", and developers "should use API key authentication through Claude Console or a supported cloud provider" ([Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)).
  A key that a customer provisions "for use by the customer's own authorized users" stays allowed, "provided the resulting usage is billed to the key owner" (same page).
- OpenAI: Sign in with ChatGPT is an "OAuth 2.0 Authorization Code flow with PKCE and OpenID Connect", "currently available to selected commercial partners through a limited trial", whose guide for websites calls the token endpoint "from your backend" ([On your website](https://developers.openai.com/siwc/website)).
  Its plan usage, for "eligible Responses API requests", is documented for "open-source and locally hosted apps", with an interest form for "a paid or remotely hosted app" ([plan usage](https://developers.openai.com/siwc/token-sharing-open-source)).
- OpenRouter: its OAuth login with PKCE gives the app "an API key tied to their account", whose requests "are billed to their own OpenRouter credits", and `required_workspace_id` "Requires the new API key to be created in this workspace", which the visitor must be able to reach ([OAuth PKCE](https://openrouter.ai/docs/use-cases/oauth-pkce)).
  The page says nothing of a key's limits or expiry.
- Vercel's AI Gateway: "Every request to AI Gateway requires Vercel authentication.
  Use an AI Gateway API key or OpenID Connect (OIDC) token."
  "Vercel deployments receive an OIDC token as `VERCEL_OIDC_TOKEN`", while an API key does not expire "unless you set an expiration date when you create them or you revoke them", and may carry a budget.
  It takes OpenAI's Chat Completions and Responses APIs and Anthropic's Messages API ([Authentication and BYOK](https://vercel.com/docs/ai-gateway/authentication-and-byok)).

The AI SDK's providers take `baseURL`, `headers` and `fetch` ([Anthropic provider](https://ai-sdk.dev/providers/ai-sdk-providers/anthropic)), and pi reaches a place that speaks a provider's API as a provider that `createProvider()` makes, whose models name the place as their `baseUrl` ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#createprovider)).
The `streamProxy()` of pi posts to a server of pi's own at `/api/stream`, which answers in pi's events ([proxy.ts#L146-L150](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/src/proxy.ts#L146-L150)), so a company's proxy that passes a provider's API through is reached through `createProvider()` instead.
Both official SDKs refuse to run in a browser without `dangerouslyAllowBrowser: true`, a key there being readable by every visitor.

Calls from the browser leave from the visitor's machine, where a company network may block the provider's domain or buffer the stream, and an endpoint private to the server's network is out of reach, as is a provider that refuses cross-origin requests, which is what a company's own proxy is for.
A proxy in R, which forwards the provider's own API with the credential added, cannot stream over HTTP, since httpuv takes a response body only whole, as "A string (or raw vector)", so streamed tokens would travel over the websocket and pause while R evaluates.

Connect's viewer OAuth integrations, such as for Azure, AWS and Databricks, give R a visitor's access token through `connectapi::get_oauth_credentials()` and the session's `Posit-Connect-User-Session-Token` header, and "OAuth refresh tokens are never returned by Connect" ([Connect](https://docs.posit.co/connect/user/oauth-integrations/)).
Anthropic's Workload Identity Federation exchanges a JWT from an identity provider, such as Entra ID, for a Claude token that acts as a service account and lasts 60 seconds to 24 hours, one hour by default ([docs](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)), which a visitor who runs R can mint as well, so it limits how long a copy works rather than who can get one.
OpenAI's and Gemini's short-lived tokens are made for their realtime and live APIs ([OpenAI](https://developers.openai.com/api/docs/guides/realtime-webrtc), [Gemini](https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens)).

</details>
