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
import Footer from './Footer';
import Acknowledgements from './Acknowledgements';

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
        element: <ZincIdSearch
          title="Zinc ID Search - Cartblanche22"
        />,
      },
      {
        path: "/search/smiles",
        element: <SmilesSearch 
          title="SMILES Search - Cartblanche22"
        />,
      },
      {
        path: "/search/random",
        element: <RandomSearch 
          title="Random Search - Cartblanche22"
        />,
      },
      {
        path: "/search/catitems",
        element: <SupplierSearch 
          title="Supplier Search - Cartblanche22"
        />,
      }
    ]

  },
  {
    path: "/results",
    element: <Results 
      title="Search Results - Cartblanche22"
    />,
  },
  {
    path: "/substance/:id",
    element: <Substance />,
    title: "Substance"
  },
  {
    path: "/tranches/:tranches",
    element: <TrancheBrowser
      title="Tranche Browser - Cartblanche22"
    />,

  },
  {
    path: "/carts",
    element: <MyCarts
      title="My Carts - Cartblanche22"
    ></MyCarts>,
  }, {
    path: "/cart",
    element: <Checkout 
      title="Checkout - Cartblanche22"
    />
  },
  {
    path: "/resetPassword/:token",
    element: <ResetPassword 
      title="Reset Password - Cartblanche22"
    />,
  },
  {
    path: "/similarity/:server",
    element: <SW 
      title="Similarity Search - Cartblanche22"
    />,
  },
  {
    path: "/patterns/:server",
    element: <Arthor 
      title="Substructure Search - Cartblanche22"
    />,
  },
  {
    path: "/acknowledgements",
    element: <Acknowledgements />,
  },
  {
    path: "/404",
    element: <Substance404 
      title="404 - Cartblanche22"
    />
  },
  {
    path: "*",
    element: <Error404 
      title="404 - Cartblanche22"
    />
  }
]);



root.render(
  <div>
    <Navigation />
    <RouterProvider router={router}/>
    <Footer></Footer>
  </div>

);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
