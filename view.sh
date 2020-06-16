pl='/mnt/c/Users/david/google-drive/coding/papmonitor/papmonitor/logs'
alias l='echo $pl/$(ls $pl | tail -n 1)'
alias tpl='l | xargs tail -n 30'
alias wpl='watch -x "$(tpl)"'
alias vpl='vim $(l)'

pp='/mnt/c/Users/david/google-drive/coding/papmonitor/data/power'
p(){
       	echo $pp/$(ls $pp | tail -n 1) 
}
tpp(){
       	p | xargs tail -n 3 
}
vpp(){
	vim $(p)
}

case $1 in 
	t)
		tpp;;
	v)
		vpp;;
esac
#vpp
