# Inertia.js Django Adapter

> **Warning:** This project is in a very early stage and depends on another early stage library and its frontend adapters called [Inertia.js](https://github.com/inertiajs/inertia).

## Requirements

This package is meant to be used in a Django application and it uses [django-rest-framework](https://www.django-rest-framework.org/)'s serializers.

```
$ pipenv install django djangorestframework django-webpack-loader
```

## Installation

There is still a few too many manual steps involved using inertia-django. I'm looking for ways (and people to help) to make the initial setup more smooth.

Install the inertia-django package from [PyPI](https://pypi.org/project/inertia-django/):

```
$ pipenv install inertia-django
```

### Webpack 📦

> **INFO:** For now it might be the easiest to take a look or clone the [example repository](https://github.com/jsbeckr/django-inertia-example).

You have to use webpack for the [Dynamic Imports Feature](https://webpack.js.org/guides/code-splitting/#dynamic-imports). The following config is borrowed from the [Django Inertia.js Example](https://github.com/jsbeckr/django-inertia-example). It uses a few plugins that are not necessary like PurgeCSS, Tailwind, MiniCSSExtract, etc. But the important ones are:

*  [Webpack Bundle Tracker](https://github.com/owais/webpack-bundle-tracker) for [Django Webpack Loader](https://github.com/owais/django-webpack-loader).
* [Vue Loader](https://github.com/vuejs/vue-loader) is optional, but there is only the [inertia-vue](https://github.com/inertiajs/inertia-vue) adapter yet.

webpack.config.js:
```javascript
const path = require("path");
const BundleTracker = require('webpack-bundle-tracker');
const VueLoaderPlugin = require('vue-loader/lib/plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

const glob = require("glob-all");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const PurgecssPlugin = require("purgecss-webpack-plugin");

class TailwindExtractor {
  static extract(content) {
    return content.match(/[A-Za-z0-9-_:\/]+/g) || [];
  }
}

module.exports = {
  mode: 'development',
  devtool: 'inline-source-map',
  // TODO: adjust the entry points to your project
  entry: ["./core/assets/js/index.js", "./core/assets/css/index.postcss"],
  output: {
    publicPath: "/static/bundles/",
    filename: "[name]-[hash].js",
    chunkFilename: '[name]-[hash].js',
    path: path.resolve('./bundles/'),
  },

  plugins: [
    new BundleTracker({ filename: './webpack-stats.json' }),
    new VueLoaderPlugin(),
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({
      filename: "[name]-[hash].css"
    }),
    new PurgecssPlugin({
      paths: glob.sync([
        // TODO: adjust the directories to your project
        path.join(__dirname, "core/assets/js/**/*.vue"),
        path.join(__dirname, "core/templates/index.html")
      ]),
      extractors: [
        {
          extractor: TailwindExtractor,
          extensions: ["html", "js", "vue"]
        }
      ]
    })
  ],

  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env'
            ],
            plugins: ["@babel/plugin-syntax-dynamic-import"]
          }
        }
      },
      {
        test: /\.vue$/,
        use: 'vue-loader'
      },
      {
        test: /\.postcss$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          { loader: 'css-loader', options: { importLoaders: 1 } },
          'postcss-loader',
        
        ]
      }
    ]
  },

  resolve: {
    extensions: ['.js', '.vue'],
    alias: {
      'vue$': 'vue/dist/vue.runtime.js',
      // TODO: adjust or remove, it's a convenient way to import js files in your components
      '@': path.resolve('core/assets/js'),
    }
  },
}
```


## Usage



### `render_inertia` function

The easiest way to render a Vue component with inertia-django is to use the `render_inertia` function. *Note:* You have to have an `Index.vue` component in your project.

```python
from inertia import render_inertia

def index(request):
    # for function views just use the render_inertia function
    return render_inertia(request, 'Index', props={'title': 'My inertia-django page'}, template_name='index.html')
```

This would be a bit much to write everytime so you can omit the `template_name` and set it in settings.py:

```python
INERTIA_TEMPLATE = 'index.html'
```

After that you just have to call:

```python
from inertia import render_inertia

def index(request):
    # for function views just use the render_inertia function
    return render_inertia(request, 'Index', props={'title': 'My inertia-django page'})
```

### `InertiaListView`

inertia-django ships with a crude implementations of the generic [ListView](https://docs.djangoproject.com/en/2.2/ref/class-based-views/generic-display/#listview):

views.py:
```python
class Index(InertiaListView):
    # Inertia supports List and DetailViews right now
    model = Contact
    serializer_class = ContactSerializer
    component_name = "Index"
```

Index.vue
```vue
<template>
  <Layout>
    <h2 class="mb-4">Contacts</h2>
    <p>User: {{shared.user.username}}</p>
    <ul>
      <li :key="contact.id" v-for="contact in contact_list">
        <inertia-link :href="'/contact/' + contact.id">
          {{contact.name}}
        </inertia-link>
      </li>
    </ul>
  </Layout>
</template>

<script>
import { InertiaLink } from "inertia-vue";
import Layout from "@/Components/Layout";

export default {
  props: ["contact_list", "shared"],
  components: { Layout, InertiaLink }
};
</script>
```

### `InertiaDetailView`

inertia-django ships with a crude implementations of the generic [DetailView](https://docs.djangoproject.com/en/2.2/ref/class-based-views/generic-display/#detailview):

views.py:
```python
class ContactView(InertiaDetailView):
    model = Contact
    serializer_class = ContactSerializer
    component_name = "Contact"
    props = {"test": True} # you can inject any props you want
```

Contact.vue:
```vue
<template>
  <Layout>
    <inertia-link href="/">Home</inertia-link>
    <h2 class="mb-4">{{contact.name}}, {{contact.first_name}}</h2>
    <p>Age: {{contact.age}}</p>
    <p>Test: {{test}}</p>
  </Layout>
</template>

<script>
import { InertiaLink } from "inertia-vue";
import Layout from "@/Components/Layout";

export default {
  props: ['contact', 'test'],
  components: { Layout, InertiaLink }
};
</script>
```

### `inertia.share` function

If you want to have some basic props that are always injected, you can `share` them between Components:

> I had to declare the `UserSerializer` in apps.py so that it is available at startup. If somebody has a better idea feel free to create an issue.

e.g. apps.py:
```python
from django.apps import AppConfig
from django.contrib.auth import get_user, get_user_model
from rest_framework import serializers
from inertia import share


def current_user(request):
    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ["username", "email"]

    return UserSerializer(get_user(request)).data


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        share('title', 'Django Inertia.js Example 🤘')
        share('user', current_user)
```

As you might have recognized `current_user` is a function. While rendering inertia-django checks if a shared property is callable and if it is, it will call that function with the current request.

## Example

~~Take a look at [this repository](https://github.com/jsbeckr/django-inertia-example) for an example of how to use this package.~~
