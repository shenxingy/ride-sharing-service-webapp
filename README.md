# erss-hwk1-jh730-xs90

## What's new

### 2025.02.03

- 用户的request后只能修改订单以及看到历史订单，不能再发起新的订单
- 用户的历史订单可以看到详细信息
- Notes(限制)
    - 一单只能有一个sharer（还没有做这个限制）
    - 允许拼车时，路线为：发起者，乘客上车点，（乘客下车点，发起者终点）后两者先后顺序不限，怎么顺路怎么来，但是需要确保下车时间都在其允许的时间限制内

## Danger Log / TODO

### Feb 6

#### Must Do
- [ ] sharer 下单填错啥的会崩溃（得加个错误提醒
- [ ] sharer requester的人数显示那一块都很蹊跷，得调整一下，但是人数筛查不在那块
- [ ] driver显示的订单必须筛查完，符合条件的才能显示
- [ ] 订单信息显示不全，解决方案（1.点击看详情。/ 2.直接把所有信息扔上去）

#### Optional

- [ ] sharer和requester有订单的时候按理来讲不应该去当司机，可以加个限制，当他想退出直接提示：您有未完成的订单，得先取消订单
- [ ] 对照danger log和todo list再看一眼，此外danger log一堆我写的中文，得翻译一波

### Feb 3

#### Must Do

- [ ] 修改订单的时候看到的内容需要和request差不多
- [ ] 我们需要给request增加id
- [ ] request可以取消

### Feb 3

#### Must Do

- [ ] The driver cannot go to the rider mode if he/she is carring a passenger; vise versa.
- [ ] 点开所有的订单可以看到详细信息(司机，sharer等)
- [ ] 一单只能有一个sharer（还没有做这个限制）
- [ ] 发起者的最晚到达时间需要比修改订单时间 + 预计到达时间 + 1min 晚
- [ ] 拼车者可以考虑退出拼车，重新搜索；拼车者确认后看到的dashboard应该和发起者类似，不过点击修改订单是回去重新搜索，即最初的dashboard

### Feb 1

#### Must Do

- [X] Add .gitignore file for __pycache__ and .vscode
- [X] Pickup Location and Dropoff Location might not be a real correct address
- [X] Passenger count can be super large
- [X] Pickup date and time is in the past
- [ ] Share or not share the ride
- [ ] Optional vehicle type
- [ ] Add arrival date and time
- [ ] Show ride id
- [ ] After ride is created, one can only view the opened rides and ride history, not request a new ride
- [ ] For the opened rides, ride owner can modify the ride.
- [ ] One dashboard, only simple version of ride is shown. User can click on the ride to see more details.
- [ ] Similar to driver, one driver can only
- [ ] Hardcode user data for testing
- [ ] Driver can update its vehicle information
- [ ] Driver can only accept one ride at a time
- [ ] Driver can see ride histories
- [ ] Driver can also see the ride details
- [ ] Driver can click finished ride
- [ ] Driver can only select rides that matched its vehicle type

#### Optional

- [ ] Time zone selection for users
- [ ] User can update their profile and password
- [ ] Add start after must entered fields


