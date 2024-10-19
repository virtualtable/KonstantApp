local function print_all(...)
	for i, v in ipairs {...} do 
		print(i, v);
	end
end

print_all(1, 2, 3, 4, 5, false, true, {}, "hello");