from os import system
import time

# Main logging class


class Logger:
    def logSim(self, threads, filters, networkNodes, params):
        """
        Simulation logging-dedicated function
        """
        nbNodes = params["nbNodes"]
        # Display network current state
        system("clear")
        currentTime = time.time()
        d = round(currentTime-params["startTime"], 3)

        #  \t+Rx_err\t+Tot Tx\t+Tot Rx\t+1b err\t+Status\t"
        #    + "Signed\t+Tx del + Rx del + Rec \t+ Tra \t+ Mask \t\t"
        #    + "+Tx err delay \t+Rx err delay\t+")

        # Monitoring purposes
        statusCount = {"OK": 0, "PASS": 0, "OFF": 0}
        errorsCount = {"TXMAX": 0, "RXMAX": 0, "TXAVG": 0, "RXAVG": 0, "1B": 0}
        totErrOneB = 0

        print("Node+ Filter    + Mask      +Txe+Rxe+Ttx+Rtx+Stat+Sign ++ "
              + "Rx del +Tx del  +Tra +Te delay+Re delay+Bus    +Node  +1be+ RSi +")

        for i in range(len(threads)):
            errc = threads[i][0].ec
            status = "OK"

            if(errc.rx_err > 127 or errc.tx_err > 127):
                status = "PASS"

            if(errc.tx_err > 255):
                status = "OFF"

            formatStr = "{:4s} {:11s} {:11s} {:3s} {:3s} {:3s} {:3s} {:3s} "
            formatStr = formatStr + "{:4s} ++ {:8s} {:8s} {:4s} "
            formatStr = formatStr + "{:8s} {:8s} {:7s} {:5s} {:5s} {:5s}"

            print(formatStr.format(
                    str(networkNodes[i][0]),
                    hex(filters[i][0]["can_id"]),
                    hex(filters[i][0]["can_mask"]),
                    str(errc.tx_err),
                    str(errc.rx_err),
                    str(errc.totTxErr),
                    str(errc.totRxErr),
                    status,
                    str(networkNodes[i][1]),
                    str(round(currentTime - errc.lastRc, 3)
                        if (params["reception"]) else " -  "),
                    str(round(currentTime - errc.lastTr, 3)
                        if (params["transmission"]) else " -  "),
                    str(errc.msgtra),
                    str(round(currentTime - errc.lastTx, 3)
                        if (params["transmission"]) else " -  "),
                    str(round(currentTime - errc.lastRx, 3)
                        if (params["reception"]) else " -  "),
                    str(errc.totRxBus),
                    str(errc.msgrec),
                    str(errc.onebyteErr),
                    str(errc.msgrecsig)))

            totErrOneB = totErrOneB + errc.onebyteErr

            statusCount[status] = statusCount[status] + 1
            if(errc.tx_err > errorsCount["TXMAX"]):
                errorsCount["TXMAX"] = errc.tx_err
            if(errc.rx_err > errorsCount["RXMAX"]):
                errorsCount["RXMAX"] = errc.rx_err

            errorsCount["TXAVG"] = errorsCount["TXAVG"] + errc.tx_err
            errorsCount["RXAVG"] = errorsCount["RXAVG"] + errc.rx_err
            errorsCount["1B"] = errorsCount["1B"] + errc.onebyteErr

        print("------------------------------------------------")
        print("Time: "+str(d)+" s")
        print("Status Nodes:"+str(nbNodes)
              + " OK:"+str(statusCount["OK"])
              + " PASS:"+str(statusCount["PASS"])
              + " OFF:"+str(statusCount["OFF"]))

        print("Errors Tx MAX:"+str(errorsCount["TXMAX"])
              + " \tAVG:"+str(errorsCount["TXAVG"]/nbNodes)
              + " \tRx MAX:"+str(errorsCount["RXMAX"])
              + "\tAVG:"+str(errorsCount["RXAVG"]/nbNodes))

        return errorsCount
