# CAAIP
## what is CAAIP?

CAAIP is Crypto Asset Accounting Improvement Proposals for short.
CAAIP try to make Crypto Asset Accounting standardize.



## CAAIP1 journal for Crypto Asset Accounting

### journal format

| |カラム名|time|platform|transaction_id|debit title|debit amount|credit title|credit amount|comment|
|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|
| |データタイプ|datetme|text|text|text|json|text|json|text|

### ex.swap


| | | |time|platform|transaction_id|debit title|debit amount|credit title|credit amount|comment|
|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|
| | | |2021-09-04 2:31:29|ethereum_kyber|0x29516785dd48a0a1393b169f2c2440985285ee1d8c7c456f03d44b73d0e6db03|SPOT|{0xb4efd85c19999d84251304bda99e90b92300bd93:105.80922530000567705}|SPOT|{0xdac17f958d2ee523a2206206994597c13d831ec7:2250}|105.80922530000567705RPL購入 2250USDT売却|
| | | |2021-09-04 2:31:29|ethereum_kyber|0x29516785dd48a0a1393b169f2c2440985285ee1d8c7c456f03d44b73d0e6db03|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|

### ex.lending


| | | |time|platform|transaction_id|debit title|debit amount|credit title|credit amount|comment|
|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|
| | | |2021-08-26 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57264|CREDIT|{0xdac17f958d2ee523a2206206994597c13d831ec7:50000}|SPOT|{0xdac17f958d2ee523a2206206994597c13d831ec7:50000}|50000USDT貸出|
| | | |2021-08-26 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57264|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|
| | | |2021-08-27 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57265|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:30000}|DEBT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:30000}|30000USDC借入|
| | | |2021-08-27 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57265|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|
| | | |2021-08-28 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57266|DEBT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:15000}|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:15000}|15000USDC返済|
| | | |2021-08-28 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57266|INTEREST|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:100}|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:100}|100USDC支払利息|
| | | |2021-08-28 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57266|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|
| | | |2021-08-29 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57267|DEBT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:15000}|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:15000}|15000USDC返済|
| | | |2021-08-29 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57267|INTEREST|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:50}|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:50}|50USDC支払利息|
| | | |2021-08-29 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57267|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|
| | | |2021-08-30 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57268|SPOT|{0xdac17f958d2ee523a2206206994597c13d831ec7:50000}|CREDIT|{0xdac17f958d2ee523a2206206994597c13d831ec7:50000}|50000USDT引出|
| | | |2021-08-30 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57268|SPOT|{0xdac17f958d2ee523a2206206994597c13d831ec7:100}|INTEREST|{0xdac17f958d2ee523a2206206994597c13d831ec7:100}|100USDC受取利息|
| | | |2021-08-30 12:21:59|ethereum_aave|0xa1d956348e7b51fc47740082e2711e59ee152b7af0787455e99f3cd684b57268|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|


### ex.liquidity mining

| |time|platform|transaction_id|debit title|debit amount|credit title|credit amount|comment|
|:----|:----|:----|:----|:----|:----|:----|:----|:----|
| |2020-09-17 1:06:17|ethereum_uniswap|0x2ef96ac3c3931ec526f79f46574ea47f4689a66f27baba70e63bb0eb4f903075|CREDIT|{0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc:0.000739829576124201}|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:17800, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2:46.868998574472280671}|17800USDCと46.868998574472280671ETHで流動性供給 0.000739829576124201UNI-V2取得|
| |2020-09-17 1:06:17|ethereum_uniswap|0x2ef96ac3c3931ec526f79f46574ea47f4689a66f27baba70e63bb0eb4f903075|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|
| |2020-09-18 1:06:17|ethereum_uniswap|0x2ef96ac3c3931ec526f79f46574ea47f4689a66f27baba70e63bb0eb4f903076|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:9633.838015911801956111, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2:24.34042978925406673407}|CREDIT|{0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc:0.0004}|0.0004UNI-V2流動性供給解除 9633.838015911801956111USDCと24.34042978925406673407ETH引出|2020-09-18 1:06:17|ethereum_uniswap|0x2ef96ac3c3931ec526f79f46574ea47f4689a66f27baba70e63bb0eb4f903076|SPOT|{0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48:8196.161984088198043889, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2:21.02856878521821393693}|CREDIT|{0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc:0.000339829576124201}|0.000339829576124201UNI-V2流動性供給解除 8196.161984088198043889USDCと21.02856878521821393693ETH引出|2020-09-18 1:06:17|ethereum_uniswap|0x2ef96ac3c3931ec526f79f46574ea47f4689a66f27baba70e63bb0eb4f903076|FEE|{ETH:0.00001}|SPOT|{ETH:0.00001}|0.00001ETH手数料支払|



