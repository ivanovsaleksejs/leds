import React, {Component} from 'react';
import './App.css';

class Button extends Component {
  constructor(props) {
    super(props)
    this.name = props.name
  }
  handleClick = (e) => {
    let props = this.props
    fetch("/backend/setsequence?sequence=" + props.sequence)
  }
  render () {
    return (
      <a className="button" onClick={this.handleClick}>{this.name}</a>
    );
  }
}

export default Button
