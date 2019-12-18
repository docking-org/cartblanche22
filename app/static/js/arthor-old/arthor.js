/****************************************
 * Copyright (c) 2018 NextMove Software *
 ****************************************/

// matches server side constants
let QueryFlags = {
  LOCK_RINGS: 0x0200,
  LOCK_CHAINS: 0x0400,
  LOCK_CHARGES: 0x0800,
  LOCK_ISOTOPES: 0x1000
};

// matches UI
let DEFAULT_FLAGS = QueryFlags.LOCK_CHARGES |
  QueryFlags.LOCK_ISOTOPES;

function Arthor(url) {
  this.url = url;
  this.query = null;
  this.table = null;
  this.flags = DEFAULT_FLAGS;
  this.type = null;
  this.time = null;
  this.count = 0;
  this.config = {};
  this.tables = {};
  this.listeners = [];

  this.configPromise = $.get(this.url + "/config").then((function (arthor) {
    return function (response) {
      arthor.config = response;
      return response;
    };
  })(this));
  this.getConfig = function () {
    return this.configPromise;
  };

  this.getHitImg = function (smiles, w, h) {
    const smarts = (this.type == 'Substructure' || this.type == 'SMARTS') ? encodeURIComponent(this.queryResponse) : '';
    let url = this.config.WebApp.DEPICTION.replace("%s", encodeURIComponent(smiles))
      .replace("%w", w)
      .replace("%h", h)
      .replace("%m", smarts);
    return 'http://arthor.docking.org/' + url.substring(2)
  };
  //gathering databases
  this.getTables = function () {
    var larthor = this;
    return $.get(this.url + "/dt/data")
      .done(function (res) {
        for (var i = 0; i < res.length; i++) {
          larthor.tables[res[i].displayName] = res[i];
        }
      });
  };

  this.meminfo = function (table) {
    return $.get(this.url + "/dt/" + encodeURIComponent(table) + "/data")
      .then(function (r) {
        return r.memInfo;
      });
  };

  this.memtouch = function (table, itype) {
    var baseurl = this.url + "/dt/" + encodeURIComponent(table)
    return $.ajax({
      url: baseurl + '/data?' + $.param({ idxtouch: itype }),
      type: 'PUT'
    });
  };

  this.memevict = function (table, itype) {
    var baseurl = this.url + "/dt/" + encodeURIComponent(table)
    return $.ajax({
      url: baseurl + '/data?' + $.param({ idxevict: itype }),
      type: 'PUT'
    });
  };

  this.notify = function () {
    if (this.table && this.type && this.query) {
      $.each(this.listeners, function (i, e) {
        e();
      });
    }
  };

  this.setTable = function (table) {
    var changed = this.table !== table;
    this.table = table;
    if (changed && arthor.config.WebApp.SearchAsYouDraw)
      this.notify();
  };

  this.setSearchType = function (type) {
    var changed = this.type !== type;
    this.type = type
    if (changed && arthor.config.WebApp.SearchAsYouDraw)
      this.notify();
  };

  this.setQuery = function (query) {
    var changed = this.query !== query;
    this.query = query;
    if (changed && arthor.config.WebApp.SearchAsYouDraw)
      this.notify();
  };

  this.addListener = function (callback) {
    this.listeners.push(callback);
  };

  this.setFlag = function (flag) {
    this.flags |= flag;
    this.notify();
  };

  this.clearFlag = function (flag) {
    this.flags = this.flags & (~flag);
    this.notify();
  };
}

/* Site specific */

var arthor = new Arthor('http://arthor.docking.org/');