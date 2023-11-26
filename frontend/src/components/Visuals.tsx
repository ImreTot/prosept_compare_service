import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "./ui/button"

const Visuals = () => {
  return (
    <div className="flex-1 p-2">
      <h2 className="text-center font-bold text-xl my-4">Дилер</h2>
      <div className="h-40 gap-4 grid">
        <Card className="">
          <CardHeader>
            <CardTitle>Сима ленд</CardTitle>
            <CardDescription>Удалитель ржавчины, 360p</CardDescription>
          </CardHeader>
          <CardContent>
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button>Cопоставить</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

export default Visuals