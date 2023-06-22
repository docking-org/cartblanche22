import React from "react";
import { useEffect, useImperativeHandle, forwardRef } from "react";
import { Col, Row, Button, Card, Table, Pagination, Navbar, Spinner, Dropdown, Container, NavLink, OverlayTrigger, Tooltip, TabContainer } from 'react-bootstrap';


const TrancheTable = forwardRef((props, ref) => {

    const [table, setTable] = React.useState([]);
    const [tranches, setTranches] = React.useState(props.tranches);
    const [axes, setAxes] = React.useState(props.axes);
    const [total, setTotal] = React.useState(0);
    const [colSums, setColSums] = React.useState([]);
    const [bigNumbers, setBigNumbers] = React.useState(props.bigNumbers);
    const [staticTotal, setStaticTotal] = React.useState(0);
    useEffect(() => {
        refreshTable();

    }, [tranches]);


    useImperativeHandle(ref, () => ({
        refreshTable() {
            refreshTable();

        },
        getCurrentTranches() {
            return getCurrentTranches();
        }
    }));


    function refreshTable() {
        let total = 0;
        let table = initTable();
        console.log(table);
        let colSums = new Array(axes[0].length).fill(0);

        tranches.map(tranche => {
            if (tranche) {
                let row = axes[0].indexOf(tranche['h_num']);
                let col = axes[1].indexOf(tranche['p_num']);

                table[col][row]['tranches'].push(tranche);
                table[col][row]['sum'] += parseInt(tranche.sum);
                if (tranche['chosen'] || tranche['chosen'] === undefined) {
                    total += parseInt(tranche.sum);
                    table[col][row]['chosen'] = true;
                }
                else if (tranche['chosen'] === false) {
                    table[col][row]['chosen'] = false;
                }

            }

        })

        table.map(row => {
            row.map(col => {
                if (col.chosen) {
                    colSums[row.indexOf(col)] += col.sum;

                }
            })

        })

        setColSums(colSums);
        setTotal(total);
        setStaticTotal(total);
        setTable(table);
    }

    useEffect(() => {
        console.log("aaa");
        setTranches(props.tranches);
    }, [props.tranches]);

    function initTable() {
        let table = [];
        for (let i = 0; i < axes[1].length; i++) {
            let row = [];
            for (let j = 0; j < axes[0].length; j++) {
                row.push({ 'tranches': [], 'sum': 0, 'chosen': true });
            }
            table.push(row);
        }
        return table;
    }

    function getCurrentTranches() {
        let t = [];

        table.map(row => {
            row.map(col => {
                col.tranches.map(tranche => {
                    t.push(tranche);
                })
            })
        })
        console.log(t);
        return t;
    }


    function getRowSum(row) {
        let sum = 0;
        row.map(col => {
            if (col.chosen) {
                sum += col.sum;
            }
        })

        return (formatSum(sum))
    }

    function formatSum(sum) {
        if (!props.bigNumbers) {
            if (sum > 1000000000) {
                return (sum / 1000000000).toFixed(1) + 'b';
            }
            if (sum > 1000000) {
                return (sum / 1000000).toFixed(1) + 'm';
            }
            if (sum > 1000) {
                return (sum / 1000).toFixed(1) + 'k';
            }
        }
        return sum.toLocaleString('en-US', { maximumFractionDigits: 2 });
    }


    function toggleTranche(row, col) {
        let newTable = [...table];
        newTable[row][col]['chosen'] = !newTable[row][col]['chosen'];
        let total = 0;
        let colSums = new Array(axes[0].length).fill(0);
        newTable.map(row => {
            row.map(col => {
                if (col.chosen) {
                    colSums[row.indexOf(col)] += col.sum;
                    total += col.sum;
                }
            })

        })
        setColSums(colSums);
        setTotal(total);
        setTable(newTable);


    }

    function toggleRow(row) {
        let newTable = [...table];
        let colSums = new Array(axes[0].length).fill(0);
        let total = 0;
        //if most of the columns are chosen, then unchoose all

        //otherwise, choose all
        let chosen = 0;
        newTable[row].map(col => {
            if (col['chosen']) {
                chosen++;
            }
        })
        let chooseAll = chosen < newTable[row].length / 2;

        newTable[row].map(col => {
            col['chosen'] = chooseAll;

        })

        newTable.map(row => {
            row.map(col => {
                if (col.chosen) {
                    colSums[row.indexOf(col)] += col.sum;
                    total += col.sum;
                }

            })

        })
        setColSums(colSums);
        setTotal(total);
        setTable(newTable);
    }

    function toggleCol(column) {
        let newTable = [...table];
        let colSums = new Array(axes[0].length).fill(0);
        let total = 0;
        //if most of the columns are chosen, then unchoose all
        //otherwise, choose all
        let chosen = 0;
        newTable.map(row => {
            if (row[column]['chosen']) {
                chosen++;
            }
        })
        let chooseAll = chosen < newTable.length / 2;
        newTable.map(row => {
            row[column]['chosen'] = chooseAll;

            row.map(col => {
                if (col.chosen) {
                    colSums[row.indexOf(col)] += col.sum;
                    total += col.sum;
                }
            })

        })
        setColSums(colSums);
        setTotal(total);
        setTable(newTable);
    }

    return (
        <div style={{ display: 'flex' }}>
            <div className="left-bar">
                <p className="title-text" style={{ transform: 'rotate(-90deg)', top: '21em', position: 'sticky' }}>LogP</p>
            </div>
            <div
                className="tranche-table"
                style={{ backgroundColor: 'grey', borderBottom: '1px solid #ccc' }}>


                <Table bordered>
                    <thead>
                        <tr>
                            <th>

                            </th>
                            {axes[0].map((axis, index) => {
                                return (
                                    <th className="cell-th v-guide" key={index + "-1"}
                                        onClick={() => toggleCol(index)}

                                    >
                                        <OverlayTrigger
                                            placement="top"
                                            delay={{ show: 250, hide: 400 }}
                                            overlay={
                                                <Tooltip id={`tooltip-${index}`}>
                                                    {axes[2][index]}
                                                </Tooltip>
                                            }
                                            key={index}

                                        >
                                            <p >{axis}</p>
                                        </OverlayTrigger>
                                    </th>
                                )
                            })}
                            <th className="last-col">
                                <div className="div-last">Totals</div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {table.map((row, rowIdx) => {
                            return (
                                <tr key={rowIdx + "-3"}>
                                    <th className="cell-th h-guide"
                                        onClick={() => toggleRow(rowIdx)}
                                    >
                                        <OverlayTrigger
                                            placement="left"
                                            delay={{ show: 250, hide: 400 }}
                                            overlay={
                                                <Tooltip id={`tooltip-${rowIdx}`}>
                                                    {axes[2][rowIdx]}
                                                </Tooltip>
                                            }
                                            key={rowIdx}
                                        >
                                            <p>{axes[1][rowIdx]}</p>

                                        </OverlayTrigger>
                                    </th>
                                    {
                                        row.map((col, colIdx) => {
                                            let sum = col.sum;
                                            //backgroud color is lighter the sum is higher
                                            // let backgroundColor = (Math.floor(255 - 255 * (Math.log(total) - 1.1 * Math.log(sum)) / (Math.log(total) - Math.log(1))));
                                            // background color is darker the sum is higher. do the opposite of above
                                            let backgroundColor = (Math.floor(255 * (Math.log(total) - 1.1 * Math.log(sum)) / (Math.log(total) - Math.log(1))));

                                            //make color lighter as the background color gets darker, so that the text is always visible
                                            let color = backgroundColor > 90 ? 'black' : '#A0A0A0';

                                            if (col.sum === 0) {
                                                backgroundColor = 'white';
                                                color = 'grey';
                                            }
                                            else {
                                                backgroundColor = `rgb(${backgroundColor}, ${backgroundColor}, ${backgroundColor})`;
                                            }

                                            if (!col.chosen) {
                                                backgroundColor = 'white';
                                                color = 'grey';
                                            }
                                            return (
                                                <OverlayTrigger
                                                    placement="top"
                                                    delay={{ show: 125, hide: 250 }}
                                                    overlay={
                                                        <Tooltip id={`tooltip-${colIdx}`}>
                                                            {axes[2][colIdx]}, {axes[2][rowIdx]}
                                                        </Tooltip>
                                                    }
                                                    key={colIdx + "-2"}
                                                >
                                                    <td
                                                        key={colIdx + "-4"}
                                                        className="cell"
                                                        style={{
                                                            backgroundColor: backgroundColor,
                                                            color: color
                                                        }}
                                                        onClick={() => toggleTranche(rowIdx, colIdx)}
                                                    >

                                                        {
                                                            formatSum(col.sum)
                                                        }

                                                    </td>
                                                </OverlayTrigger>
                                            )
                                        }
                                        )
                                    }
                                    <th className="last-col">
                                        <div className="div-last">
                                            {
                                                getRowSum(row)
                                            }
                                        </div>
                                    </th>

                                </tr>
                            )
                        })}

                    </tbody>
                    <tfoot>
                        <tr>
                            <th>
                                <div>Totals</div>
                            </th>
                            {
                                colSums.map((col, index) => {
                                    return (
                                        <th className="cell-th v-guide"
                                            key={index + "-5"}
                                        >


                                            <p>{formatSum(col)}</p>

                                        </th>
                                    )
                                })
                            }
                            <th className="last-col">
                                <div className="div-last">= {formatSum(total)}</div>
                            </th>


                        </tr>
                    </tfoot>

                </Table>
            </div>
        </div >

    )
})


export default TrancheTable;