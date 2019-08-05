import React, {Component} from 'react';
import 'fetch'
import './App.css';
import Button from './Button.js'
import config from './config.json'

class App extends Component {
  constructor(props) {
    super(props)
    this.buttons = config.buttons
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    }
  }
  render () {
    let buttons = this.buttons.map((item, key)=>
      <Button name={item.title} key={key} sequence={item.name} />
    )
    return (
      <div className="main">
        {buttons}
      </div>
    );
  }
}

export default App;
