# Model access: providers, gateways and credentials
Status: settled on 2026-11-13. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): where the assistant's calls to a model go, how they are authenticated, which models a deployment offers and who picks among them, through four blockr options, and the model's settings.
It shapes the Work items of that part that send the calls, let a visitor use their own key and let a visitor log in.
The loop that makes the calls stays with the part, the state that keeps each thread's pick of the model is [The assistant's state](Rewrite-1.4.3)'s, and the chat that asks for a key and offers the pick is [The assistant's chat](Rewrite-1.4.4)'s.

## What must hold

1. A deployment chooses where the assistant's calls go, how they are authenticated and which models it offers through its blockr options alone, without changing any code of the assistant.
2. A demo works for visitors who have no account with any provider or gateway.
3. No call to a model goes through the session's R process.
4. A visitor's own key never reaches the board, a saved board, R, or browser storage that outlives the page.

## Today

Today's assistant calls its model from the session's R process, through the ellmer chat that the blockr option `chat_function` gives, with whatever credential that function reads in R's environment ([Assistant as a plugin](Rewrite-1.4#today)).
So a deployment reaches any provider that ellmer has a chat function for, such as AWS Bedrock through `chat_aws_bedrock()`.
Both apps that use it chat with OpenAI, with a key in `OPENAI_API_KEY`.

## Proposal

### Where the calls go

From the browser, these three look alike, since each is a base URL that speaks a provider's API and takes a credential where it needs one:

- A provider, such as OpenAI or Anthropic.
- A gateway, such as OpenRouter or Vercel's AI Gateway, which reaches the models of many providers through one API and one account.
- A company's own proxy, which holds the provider's key inside the company's network and decides who may call.

So the assistant reaches all three in one way, through a provider that pi's `createProvider()` makes for the base URL (notes).
The assistant speaks OpenAI's Responses and Chat Completions APIs and Anthropic's Messages API.
Each is a protocol of its own, the shape of a call and of the stream that answers it, and any base URL may speak it, not only its maker's.
Vercel's AI Gateway speaks all three, and so does OpenRouter for every model that it serves for chat (notes).
So a base URL that speaks one of them takes configuration alone (condition 1).
A company's own proxy, which the company runs beside the app, is reached as a gateway is, and one that needs no key from the page takes none (How a call is authenticated).

A page calls OpenAI's and Anthropic's APIs directly, the latter with the header by which a page opts in, as calls from a page with real keys showed.
OpenRouter and Vercel's AI Gateway answer a page as well, as probes with a dummy key showed ([Assistant as a plugin](Rewrite-1.4)).
Some of the providers that ellmer reaches today are out of a page's reach, and a deployment reaches them through a gateway or a company's own proxy:

- A provider whose API the assistant does not speak, such as AWS Bedrock, which pi does not call from a browser (notes).
- A provider that refuses a page's cross-origin calls, such as Ollama's cloud, which refused a page's preflight in a probe (notes).
- A model served on a network that the server reaches and the visitor's browser does not.

A company's network may also keep its visitors' browsers from a provider's domain, since each call leaves from the visitor's machine (notes).
Such a company reaches the provider through its own proxy, and each deployment finds out whether it needs one as it is set up.

A deployment sends every call to one base URL.
Today a `chat_function` list may mix providers, each entry with a credential of its own (Who picks the model).
After the switch, a gateway gives that mix through one base URL and one key.
Several base URLs in one deployment are later work, which nothing here rules out.

The plugin names no app in its calls, since no use needs a base URL to know which app calls it.
The agent of pi names pi to OpenRouter unless it is told otherwise, so the plugin gives it `null` as its `identity` (notes).

No call goes through the session's R process (condition 3).
R runs one request at a time ([Wire protocol](Rewrite-1.1.9#one-request-at-a-time)), so a model call there would hold up evaluation for its whole length, and httpuv cannot stream a response (notes).
A key held in R would be no safer either, since a visitor can read it through a block that takes code, except on a board where no visitor runs R (How a call is authenticated).

### How a call is authenticated

The loop takes its credential through `getApiKey`, a function that pi calls for each request, so that each way below feeds it and the loop knows none of them ([Assistant as a plugin](Rewrite-1.4#proposal)).
None of these ways suits every deployment, and which one a call takes follows from the blockr options (The blockr options):

| Way | The hoster provides | A visitor needs | Who pays | What a visitor can copy |
|---|---|---|---|---|
| The deployment's key | A key, in the blockr option `assistant_api_key`, which the plugin reads through `CoreApi.blockrOption()` | Nothing | The hoster | The hoster's key, which works until the hoster revokes it |
| No key, for a base URL that needs none, such as a company's own proxy | `"none"` in `assistant_api_key` | Nothing | The hoster | Nothing |
| The visitor's own key | Nothing | A key of their own, which they trust the app with | The visitor | Their own key, and nothing of the hoster's |
| A login with a service that offers one, such as OpenRouter | The service's base URL, in the blockr option `assistant_base_url` | An account with that service | The visitor | A key on their own account, which works until they revoke it, since the login sets no expiry (notes) |
| The hosting platform's integration, such as Connect's | Later | Later | Later | Later |

Where the deployment sets a key, every call uses it.
Where it sets `"none"`, no call carries a key.
In both cases the chat asks for nothing.
Otherwise the chat asks the visitor for their own key, and offers a login beside it where the base URL belongs to a service that offers one, such as OpenRouter.
So no blockr option lists the ways, and the hosting platform's integration, once it comes, will follow from the platform that the app runs on.

- The deployment's key is the easiest way and the least safe.
  Any visitor who can use the assistant can take it from the page.
  Where a visitor can run R, they can take it from R as well, today as after the switch: through a block that takes their code, as core's subset block takes its `subset` and `select` ([R/transform-subset.R#L29-L31](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-subset.R#L29-L31)), and through the assistant's request that runs the R its model writes ([Assistant as a plugin](Rewrite-1.4#proposal)).
  There a key in the browser only makes that visible.
  Where the load lock and the board lock are both on and every block is locked, no visitor runs R, since R evaluates only the opening board, whatever a client sends ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-must-hold)), and refuses the assistant's request ([Assistant as a plugin](Rewrite-1.4#proposal)).
  There the key in the page is exposed as the key in R is not, so a deployment that must keep its key from such visitors holds it in its own proxy instead, which the page calls with no key and which decides who may call.
  Short-lived tokens would not change who can take one: OpenAI's and Gemini's serve only their realtime and live APIs, and a visitor who runs R can mint Anthropic's as R would (notes).
  Limiting the key stays the deployment's job ([State in JS](Rewrite-1#proposal)), which matters most for an app on the public internet, whose visitors are anyone.
  It suits a demo, whose visitors need no account (condition 2).
  The plugin reads it only from `assistant_api_key`, never from a variable that a provider's own clients read, such as the `OPENAI_API_KEY` that ellmer reads in R, so that a key set for code in R reaches no browser unless the deployment hands it over.
- No key suits a company's own proxy that lets anyone on the company's network call, since the proxy holds the provider's key itself.
  The plugin then sends no `Authorization` header.
  So the proxy's answer to a page's preflight need not allow that header, as it would have to for a placeholder key.
  Such a proxy trusts the visitor's network position, which is what CORS protects, so it allows only the app's origin.
  If it allowed every origin, any page that someone on the network opens could call it through their browser, at the company's cost.
- The visitor's own key stays in the page's memory: the visitor types it into the assistant's panel, and the plugin hands it to pi for each call.
  It stays out of a board option, whose value the board saves once someone sets it ([Board options and blockr options](Rewrite-1.1.13#the-two-kinds)), and out of browser storage that outlives the page, which every page served from the same origin can read (condition 4).
  So the visitor types the key again after each reload.
- A login works only with a service that offers one to a web page: OpenRouter does, OpenAI offers its own to selected partners for now, and Anthropic forbids one (notes).
  So the plugin offers it where the base URL is OpenRouter's, `https://openrouter.ai/api/v1`.
  It opens the login in a window of its own, whose callback hands the code back to the page, since sending the page itself to OpenRouter would reload the app.
  Every visitor then needs an account with that service, which a demo cannot ask of its visitors.
  The key that a login gives is the visitor's own, so it stays in the page's memory, as a typed key does, and a reload asks for the login again.
  OpenRouter's login can also make its key in a workspace of the hoster's, through `required_workspace_id`, and OpenRouter bills an organization's keys to the organization's credits (notes), which would let a company pay for the calls of its members, each logging in with an account in its organization.
  That is later work, which nothing here rules out.
- The hosting platform's integration is later work, for which this page leaves room.
  The platform vouches for the visitor or for the deployment, so that the app holds no key of the hoster's, as Connect's AI Gateway takes a short-lived credential of Connect's own for Anthropic's API and puts the real key on the call (notes).
  Only R gets such a credential, since Connect hands it and the visitor's session token to the app's server alone, so R would pass it on to the page, while the calls still leave from the page (condition 3).

Of the base URLs that a page reached in the probes, OpenAI alone puts no CORS header on the 401 with which it refuses a key, so a page sees that refusal as a failed connection ([Assistant as a plugin](Rewrite-1.4)), and the chat says that the key may be wrong ([The assistant's chat](Rewrite-1.4.4#the-credential)).

### Who picks the model

Today the blockr option `chat_function` gives one of ellmer's chat functions, which fixes the model, or a named list of them ([Assistant as a plugin](Rewrite-1.4#today)).
From a list, the user picks one through core's board option `llm_model`, which the dock's options sidebar shows, and the board saves the pick by its name.
The clinical data explorer's script offers three of OpenAI's models that way, named by their ids, while blockr.uat's chats with ellmer's default.
Both options go, since they were shaped for ellmer's chat functions ([Assistant as a plugin](Rewrite-1.4#proposal)), while what they let a deployment choose carries over.

The models that a deployment offers are those it names in `assistant_models`, and the first is the default (The blockr options):

- One model fixes the model for every thread, and the chat offers no pick.
- Several let the user pick one in the chat for each thread.
- Where the deployment names none, the chat offers the models that the base URL lists for the key, and keeps those that take tools where the list says which do, the first that it keeps being the default.

OpenAI's list says nothing of what a model takes, so the issue that sends the calls settles how the plugin keeps the models that take tools from it, such as by their ids (notes).
Anthropic's and OpenRouter's lists put the newest model first, while OpenAI's and Vercel's follow no documented order (notes), so a deployment names its models where the default matters.
A call to a model that the visitor's account cannot reach fails as any call does ([The assistant's chat](Rewrite-1.4.4#what-fails)).
Where the base URL gives no list, as a company's own proxy may not, or one in which no model takes tools, the chat says so and offers no model, so a deployment on such a base URL names its models, while a list refused for its key goes as any refused key does ([The assistant's chat](Rewrite-1.4.4#what-fails)).

Each thread keeps its own pick of the model, in the assistant's state, so that it talks to the same model after a reload and in a saved board ([The assistant's state](Rewrite-1.4.3#the-state)).
A new thread takes the pick of the thread that is open as it is added, so that it goes on with the last pick, as threads do under today's board option.
Where no thread is open, a pick goes to the thread that the first message adds.
A thread that nobody picked a model for talks to the default.
A pick in the chat's footer sets the model of the open thread alone, through the command `blockr.assistant-set_model`.
It is a command of the assistant's own, as every change to its state is, so that a pick takes no undo step and works on a locked board, which core's command for a plugin's state would not ([The assistant's state](Rewrite-1.4.3#commands)).
Where the deployment does not offer a thread's pick, the chat says so and the thread talks to the default, while the pick stays in the state, so that the thread talks to its model again under a deployment that offers it.
The chat's footer offers the pick where the deployment offers more than one model or names none ([The assistant's chat](Rewrite-1.4.4#the-model)).
A default of the visitor's own for new threads, such as one kept in the browser's local storage, is later work, which nothing here rules out.

### The model's settings

Today no app sets the model's settings, such as its reasoning effort, so every call gets the provider's defaults.
Today's assistant builds its chat with `ctor(system_prompt = "")` ([R/ext-server.R#L483](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L483)), which passes no `params`.
The chat function that blockr.uat takes, core's default, sets none of its own ([blockr.core R/board-option.R#L660-L662](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L660-L662)), and neither do those of the clinical data explorer's script.
After the switch, the plugin's code fixes the settings, such as the `thinkingLevel` of pi's agent, which starts at `medium`.
Today's calls send no reasoning effort, so each model reasons at its own default, which OpenAI gives as `medium` for its current models, while pi sends an effort on every call to a model that reasons, `none` for its level `off`, which GPT-6 Astra refuses (notes).
A change to the settings changes what the model does, so after `js-state` has merged into main, it merges only once [The assistant's benchmark](Rewrite-1.8.1#what-must-hold) has compared it with the version before it.

Letting someone change the settings is later work, which nothing here rules out, such as a pick of the thinking level for each thread beside its pick of the model.
A setting for a thread would go in the assistant's state, as its pick of the model does, since a setting of a plugin's own goes there first ([Places the dock offers plugins](Rewrite-1.2.4#settings)).
A setting for a deployment would be a blockr option, as the models that it offers are.

### The blockr options

A deployment sets where the calls go, how they are authenticated and which models it offers through four blockr options, each a string that an environment variable can give, so that a deployment such as Connect sets them without touching the app script ([Board options and blockr options](Rewrite-1.1.13#blockr-options)):

| Blockr option | What it holds | Where it is unset |
|---|---|---|
| `assistant_base_url` | The base URL that the calls go to | OpenAI's API, which today's default chat function calls |
| `assistant_api` | The API that the base URL speaks, by pi's name for it: `"openai-responses"` for OpenAI's Responses API, `"openai-completions"` for its Chat Completions API, or `"anthropic-messages"` for Anthropic's Messages API | `"openai-responses"`, since OpenAI's base URL speaks the Responses API |
| `assistant_api_key` | The deployment's key, or `"none"` for a base URL that needs no key | The visitor authenticates (How a call is authenticated) |
| `assistant_models` | The models offered, the first being the default, separated by commas in an environment variable | The chat offers the models that the base URL lists for the key, the first being the default (Who picks the model) |

A demo on OpenAI's models then sets two, `BLOCKR_ASSISTANT_API_KEY` and, say, `BLOCKR_ASSISTANT_MODELS=gpt-5.4`, and an app for visitors who log in with OpenRouter sets two, `BLOCKR_ASSISTANT_BASE_URL=https://openrouter.ai/api/v1` and `BLOCKR_ASSISTANT_API=openai-completions`, the API that pi's own catalog uses for OpenRouter (notes).
The plugin does not work out which API a base URL speaks, so a deployment that sets another base URL sets `assistant_api` too, unless that base URL speaks the Responses API.
It hands the value to pi unchanged, as the `api` of each model that it builds (notes), so that the option, the page and the code name each API alike.
The plugin reads the four through `CoreApi.blockrOption()`, which asks R for their values.
It takes an array in `assistant_models` as it is, and splits a string at its commas.
An environment variable gives a string, and so does an R option that names one model, since R writes a blockr option of length one bare ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).

### Today's deployments across the switch

A deployment of today's assistant moves to the blockr options above at the switch:

- A deployment that gives today's assistant its key in `OPENAI_API_KEY` sets the key in `BLOCKR_ASSISTANT_API_KEY` too, since the plugin reads no variable of a provider's own clients (How a call is authenticated).
  Without it, the chat asks each visitor for a key of their own.
- A script that sets `chat_function` drops it and names the models of its entries in `assistant_models`, as `BLOCKR_ASSISTANT_MODELS=gpt-5.4,gpt-5.4-nano` names two of OpenAI's.
- A deployment that leaves `chat_function` unset, as blockr.uat's does, names the model that it chats with in `assistant_models`, since OpenAI's list follows no documented order (Who picks the model).
- A chat function of another provider becomes that provider's base URL in `assistant_base_url`, with `assistant_api` where that base URL does not speak the Responses API.
  Where a page cannot call the provider, the base URL is a gateway's or a proxy's instead (Where the calls go).

A board saved today opens with none of its threads, and the conversion leaves out the value of `llm_model` ([The assistant's state](Rewrite-1.4.3#boards-saved-today)).

## Open questions

None.

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
- Fetched without a key, OpenRouter's list held 470 models.
  They ran from the newest `created` to the oldest.
  Of these, 383 named `/api/v1/chat/completions`, `/api/v1/responses` and `/api/v1/messages` alike in `endpoints`.
  The other 87, each with an id that ends in `:batch`, named only `/api/v1/batches`, and 83 of them listed `tools`, so the plugin keeps only the models whose `endpoints` name the path of its API.
- Vercel's `GET https://ai-gateway.vercel.sh/v1/models` "requires no authentication", gives each model's `type`, such as `language` or `embedding`, and names models as `creator/model-name` ([Models and providers](https://vercel.com/docs/ai-gateway/models-and-providers)).
  Fetched the same day, it held 511 models, of which 326 had the `type` `language`, and 308 of those had the tag `tool-use` in `tags`, while no property said which API serves a model.
  Every model carried the same `created`, and the list ran neither by that nor by id.
- OpenRouter: "API usage from any organization key is billed to the organization's credit pool" ([Organization management](https://openrouter.ai/docs/cookbook/administration/organization-management)).
  A key's `limit` is "the spend limit in USD, or `null` if the key has no limit", and its `expires_at` is null "if the key never expires", while "An expiration can't be added to an existing key" ([API key audit](https://openrouter.ai/docs/cookbook/administration/api-key-audit)).

The package pi-ai reaches a base URL that speaks a provider's API through a provider that `createProvider()` makes, whose models name that base URL as their `baseUrl` ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#createprovider)).
The `streamProxy()` of pi posts to a server of pi's own at `/api/stream`, which answers in pi's events ([proxy.ts#L146-L150](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/src/proxy.ts#L146-L150)), so a company's proxy that passes a provider's API through is reached through `createProvider()` instead.

Read on 2026-11-13 in pi's READMEs at `e3da248`:

- Providers of pi "internally share API implementations (the wire protocols): Anthropic models use `anthropic-messages`, OpenAI uses `openai-responses`, while xAI, Groq, Cerebras, OpenRouter, and most others share `openai-completions`" ([Providers and Models](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#providers-and-models)).
  So pi speaks each API behind one call, while a base URL outside its catalog needs the app to name its API, as `createProvider()` takes it.
- The package pi-ai calls Amazon Bedrock from Node alone: "Amazon Bedrock (`bedrock-converse-stream`) is not supported in browser environments" ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#browser-usage)).
- A model of pi is an object that names its `api`, `baseUrl`, `reasoning`, `input`, `contextWindow` and `maxTokens` ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#createprovider)), which `getBuiltinModel()` gives for the models of pi's catalog ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#static-catalog-reads)).
  So the plugin builds one for a model that the catalog lacks, as behind a company's own proxy, with defaults that the issue that sends the calls sets.
  Its `input` holds `"image"`, so that the plots of `inspect_results` reach the model, as today's assistant sends them to every model through `ellmer::content_image_file()` ([R/utils-plot.R#L62-L64](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/utils-plot.R#L62-L64)).
  Where such a model takes no images, its server may refuse the call that carries a plot, and every later call of the thread, since the plot stays in the thread's history, as it would with today's assistant.
  A blockr option that names the models that take no images, for which pi replaces each image with "(tool image omitted: model does not support images)", is later work for a deployment that needs it, which nothing here rules out.
- "Every provider declares auth; keyless local servers resolve as configured with no key", through an `auth` whose `resolve()` gives `{ auth: {} }` ([createProvider()](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#createprovider)).
- The agent of pi takes a `thinkingLevel` in its initial state, one of `off`, `minimal`, `low`, `medium`, `high`, `xhigh` and `max` ([Agent Options](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/README.md#agent-options)), and pi-ai turns a level into each provider's own control, such as OpenAI's `reasoningEffort` ([Thinking/Reasoning](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#thinkingreasoning)).
  For a model that reasons, pi sends an effort on every call to the Responses API, `none` for the level `off` unless the model maps `off` to another ([openai-responses.ts#L408-L410](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/src/api/openai-responses.ts#L408-L410)), as the built package of pi-ai 1.5.2 does too.
  It leaves the effort out only for a model whose `reasoning` is false, and then leaves out the encrypted reasoning that it otherwise asks back for the next call (same file).
- The agent of pi names pi to OpenRouter, through `HTTP-Referer: https://pi.dev` and `X-OpenRouter-Title: pi`, unless it is given an `identity` of the app's own, or `null` to send none ([Client Identity](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#client-identity), [Agent Options](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/README.md#agent-options)).

OpenAI's guide to reasoning, read on 2026-11-13, says that "Defaults are also model-dependent rather than universal", and that its gpt-5.5 "defaults to medium reasoning effort".
It says too that "GPT-6 Astra does not support none reasoning effort", and that setting the effort "to none returns HTTP 400".
It also says that "Chat Completions does not support function calling with GPT-6 Astra or GPT-6.1 Sol" ([Reasoning](https://developers.openai.com/api/docs/guides/reasoning)).

Ollama's cloud takes Chat Completions at `https://ollama.com/v1` and Anthropic's Messages API at `https://ollama.com/v1/messages` ([OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility), [Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility)).
Probed on 2026-11-13 with a page's `Origin`, it answered the preflight of both with a 405 and no CORS header, and a call with a dummy key with a 401 that carried none either.

Calls from the browser leave from the visitor's machine, where a company network may block the provider's domain or buffer the stream.
A base URL private to the server's network is out of their reach, and so is a provider that refuses cross-origin requests, which is what a company's own proxy is for.
A proxy in R, which forwards the provider's own API with the credential added, cannot stream over HTTP, since httpuv takes a response body only whole, as "A string (or `raw` vector)" ([R/httpuv.R#L526-L527](https://github.com/rstudio/httpuv/blob/5e3d6827c284210b6a7cba7009cf73beb2e03525/R/httpuv.R#L526-L527)), so streamed tokens would travel over the websocket and pause while R evaluates.

Connect's viewer OAuth integrations, such as for Azure, AWS and Databricks, give R a visitor's access token through `connectapi::get_oauth_credentials()` and the session's `Posit-Connect-User-Session-Token` header, and "OAuth refresh tokens are never returned by Connect" ([Connect](https://docs.posit.co/connect/user/oauth-integrations/)).
Connect puts that header on the requests that reach the app's server, so a page cannot make the exchange itself.

Connect's AI Gateway, in early access, "sends large language model (LLM) requests from your content to the provider", for Anthropic through an Anthropic integration and for Amazon Bedrock through an AWS integration, while "Requests to other LLM providers do not go through the AI Gateway" ([AI Gateway](https://docs.posit.co/connect/user/ai-gateway/)).
For Anthropic, "ANTHROPIC_API_KEY contains a short-lived Connect credential rather than the real Anthropic key", and "Connect substitutes the real key on the outbound request" ([Integrations](https://docs.posit.co/connect/user/oauth-integrations/)).
Content that serves several visitors from one process "must send each request with the session token of the viewer that the request is for", and Connect counts a request without one against the content's owner (AI Gateway).
The docs' example puts the gateway under Connect's own host, as `https://connect.example.com/__gateway__/anthropic/<guid>`, where Connect serves its content as well, so a page that Connect serves would call it from its own origin, with no CORS involved.

Anthropic's Workload Identity Federation exchanges a JWT from an identity provider, such as Entra ID, for a Claude token that acts as a service account and lasts 60 seconds to 24 hours, one hour by default ([docs](https://platform.claude.com/docs/en/manage-claude/workload-identity-federation)), which a visitor who runs R can mint as well, so it limits how long a copy works rather than who can get one.
OpenAI's and Gemini's short-lived tokens are made for their realtime and live APIs ([OpenAI](https://developers.openai.com/api/docs/guides/realtime-webrtc), [Gemini](https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens)).

</details>
