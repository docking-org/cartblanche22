import React from 'react';
import ReactDOM from 'react-dom/client';

import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import reportWebVitals from './reportWebVitals';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';


import App from './App';
import Navigation from './Navbar';

import Results from './Search/Results';
import ZincIdSearch from './Search/ZincIdSearch';
import SmilesSearch from './Search/SmilesSearch';
import RandomSearch from './Search/RandomSearch';
import SupplierSearch from './Search/SupplierSearch';
import Substance from './Substance/Substance';
import TrancheBrowser from './Tranches/TrancheBrowser';
import MyCarts from './Cart/MyCarts';
import Checkout from './Cart/Checkout';
import ResetPassword from './Users/ResetPassword';
import SW from './Similarity/SW';
import Arthor from './Substructure/Arthor';
import Substance404 from './Errors/Substance404';
import Error404 from './Errors/Error404';

const root = ReactDOM.createRoot(document.getElementById('root'));

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/search",
    children: [
      {
        path: "/search/zincid",
        element: <ZincIdSearch />,
      },
      {
        path: "/search/smiles",
        element: <SmilesSearch />,
      },
      {
        path: "/search/random",
        element: <RandomSearch />,
      },
      {
        path: "/search/catitems",
        element: <SupplierSearch />,
      }
    ]

  },
  {
    path: "/results",
    element: <Results />,
  },
  {
    path: "/substance/:id",
    element: <Substance />,
    title: "Substance"
  },
  {
    path: "/tranches/:tranches",
    element: <TrancheBrowser />,

  },
  {
    path: "/carts",
    element: <MyCarts></MyCarts>,
  }, {
    path: "/cart",
    element: <Checkout />
  },
  {
    path: "/reset_password/:token",
    element: <ResetPassword></ResetPassword>,
  },
  {
    path: "/similarity/:server",
    element: <SW />,
  },
  {
    path: "/patterns/:server",
    element: <Arthor></Arthor>,
  },
  {
    path: "/404",
    element: <Substance404></Substance404>
  },
  {
    path: "*",
    element: <Error404 />
  }

  // {
  //   path: "/Substructure",
  //   element: <Substructure />,
  // },
  // {
  //   path: "/Substances",
  //   element: <Substances />,
  // }
]);



root.render(
  <div>
    <Navigation />
    <RouterProvider router={router} />
  </div>

);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
