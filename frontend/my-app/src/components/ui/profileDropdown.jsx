import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { CircleUserRound,User, UserRound ,LogOut} from "lucide-react";
import { useRouter } from "next/navigation";

function Component({user_id}) {
    const router = useRouter()
    // id=localStorage.getItem("user_id")
    const handleLogout=()=>{
        localStorage.removeItem("user_id")
        router.push("/")
    }
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button size="icon" className="bg-slate-800" aria-label="Open account menu">
          <User size={21} strokeWidth={2} aria-hidden="true" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="ml-30 max-w-64">
        <DropdownMenuLabel className="flex flex-col">
          <span className="text-sm">Signed in as</span>
          <span className="text-md text-foreground">+91 {user_id}</span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout}  className=" justify-between flex text-md cursor-pointer text-red-500 hover:bg-red-100 hover:text-red-600 focus:bg-red-100 focus:text-red-600">
            Logout
        <LogOut size={18} className="" />
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export { Component };
