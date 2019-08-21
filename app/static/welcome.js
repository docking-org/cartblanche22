const e = React.createElement;
class Welcome extends React.Component {
  state = {}

  componentDidMount() {
    var xhr = new XMLHttpRequest();
    var json_obj, status = false;
    xhr.open("GET", "https://jsonplaceholder.typicode.com/photos/", true);
    xhr.onload = function (e) {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          var json_obj = JSON.parse(xhr.responseText);
          status = true;
          this.setState({ json_obj });
        } else {
          console.error(xhr.statusText);
        }
      }
    }.bind(this);
    xhr.onerror = function (e) {
      console.error(xhr.statusText);
    };
    xhr.send(null);
  }

  render() {
    return (
      <div>
          <img src= {this.state.json_obj ?  this.state.json_obj[0].url : 'loading...'}></img>
      </div>
    );
  }
}
const domContainer = document.querySelector('#welcome_container');
ReactDOM.render(e(Welcome), domContainer);
);
