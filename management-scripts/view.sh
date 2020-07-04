#!/usr/bin/sh
recent(){
       	echo $1/$(ls $1 | tail -n 1) 
}
tailRecent(){
       	recent $1 | xargs tail -n 30
}
vimRecent(){
	vim --clean $(recent $1)
}

power='/mnt/c/Users/david/google-drive/coding/papmonitor/data/power'
recentPower(){
	recent $power
}
tailRecentPower(){
	tailRecent $power
}
vimRecentPower(){
	vimRecent $power
}

log='/mnt/c/Users/david/google-drive/coding/papmonitor/papmonitor/logs'
recentLog(){
	recent $log
}
tailRecentLog(){
	tailRecent $log
}
vimRecentLog(){
	vimRecent $log
}

case $1 in 
	tp)
		tailRecentPower;;
	vp)
		vimRecentPower;;
	tl)
		tailRecentLog;;
	vl)
		vimRecentLog;;
	*)
		echo "invalid selection: $1\ntp|vp|tl|vl"
		exit 1
esac
