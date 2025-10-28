! For loop
do i = 0, 100, 1
  print*, "hello"
end do
! If statement
if (i == 1) then
  print*, 1
end if
! While loop
do while (i < 1)
  print*, i
  i = i+1
end do
! Integer variable
integer :: integer_var
integer_var = 1
! Float variable
real :: floatingpoint
floatingpoint = 1.0
! String variable
character(len=20) :: string
string = "string"
! Boolean variable
logical :: boolean
boolean = .true.
