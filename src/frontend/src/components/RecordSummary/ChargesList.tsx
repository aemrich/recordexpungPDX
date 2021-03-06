import React from 'react';

interface Props {
  eligibleCharges: string[];
  totalCharges: number;
}

export default class ChargesList extends React.Component<Props> {
  render() {

    const listItems = this.props.eligibleCharges.map(((chargeName:string, index:number) => {
      return <li className="bt b--light-gray pt1 mb1">{chargeName}</li>
    }));

    return (
      <div className="w-100 w-50-ns w-33-l br-ns b--light-gray mr3-ns pr3 mb3">
        <h3 className="bt b--light-gray pt2 mb3"><span className="fw7">Charges</span> {this.props.totalCharges}</h3>
        <div>
          <span className="fw8 green mb2">{"Charges eligible now"} </span> <span className="fw8">{"(" + this.props.eligibleCharges.length + ")"}</span>
        </div>
        <ul className="list mb3">
         {(listItems.length > 0 ? listItems : "None")}
        </ul>
      </div>
      )
    }
}